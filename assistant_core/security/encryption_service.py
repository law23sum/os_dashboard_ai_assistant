"""
Encryption Service - Data encryption, key management, and cryptographic operations
Handles encryption at rest, in transit, and key lifecycle management
"""

import asyncio
from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict, field
from enum import Enum
import json
import logging
from pathlib import Path
import uuid
import hashlib
import secrets
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
import os


class EncryptionType(Enum):
    """Encryption types"""
    AES_256_GCM = "aes_256_gcm"
    AES_256_CBC = "aes_256_cbc"
    FERNET = "fernet"
    RSA_2048 = "rsa_2048"
    RSA_4096 = "rsa_4096"
    CHACHA20_POLY1305 = "chacha20_poly1305"


class KeyType(Enum):
    """Cryptographic key types"""
    SYMMETRIC = "symmetric"
    ASYMMETRIC_PRIVATE = "asymmetric_private"
    ASYMMETRIC_PUBLIC = "asymmetric_public"
    DERIVED = "derived"
    MASTER = "master"


class KeyStatus(Enum):
    """Key lifecycle status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    COMPROMISED = "compromised"
    EXPIRED = "expired"
    REVOKED = "revoked"


@dataclass
class EncryptionKey:
    """Encryption key metadata"""
    key_id: str
    key_type: KeyType
    encryption_type: EncryptionType
    status: KeyStatus
    created_at: datetime
    expires_at: Optional[datetime] = None
    key_material: Optional[bytes] = None  # Encrypted key material
    public_key: Optional[bytes] = None
    algorithm: str = ""
    key_size: int = 0
    usage: List[str] = field(default_factory=list)  # encrypt, decrypt, sign, verify
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            **asdict(self),
            "key_type": self.key_type.value,
            "encryption_type": self.encryption_type.value,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "key_material": base64.b64encode(self.key_material).decode() if self.key_material else None,
            "public_key": base64.b64encode(self.public_key).decode() if self.public_key else None
        }


@dataclass
class EncryptionOperation:
    """Encryption operation record"""
    operation_id: str
    operation_type: str  # encrypt, decrypt, sign, verify
    key_id: str
    encryption_type: EncryptionType
    timestamp: datetime
    data_size: int
    success: bool
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            **asdict(self),
            "encryption_type": self.encryption_type.value,
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class EncryptedData:
    """Encrypted data container"""
    data_id: str
    encrypted_data: bytes
    encryption_type: EncryptionType
    key_id: str
    iv: Optional[bytes] = None  # Initialization vector
    tag: Optional[bytes] = None  # Authentication tag for AEAD
    salt: Optional[bytes] = None  # Salt for key derivation
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            **asdict(self),
            "encryption_type": self.encryption_type.value,
            "encrypted_data": base64.b64encode(self.encrypted_data).decode(),
            "iv": base64.b64encode(self.iv).decode() if self.iv else None,
            "tag": base64.b64encode(self.tag).decode() if self.tag else None,
            "salt": base64.b64encode(self.salt).decode() if self.salt else None,
            "created_at": self.created_at.isoformat()
        }


class KeyManager:
    """Cryptographic key management"""
    
    def __init__(self, master_key: Optional[bytes] = None):
        self.keys: Dict[str, EncryptionKey] = {}
        self.master_key = master_key or self._generate_master_key()
        self.key_derivation_iterations = 100000
        
        self.logger = logging.getLogger(__name__)
    
    def _generate_master_key(self) -> bytes:
        """Generate master key for key encryption"""
        return secrets.token_bytes(32)  # 256-bit master key
    
    async def generate_key(self, encryption_type: EncryptionType,
                          usage: List[str], expires_in_days: Optional[int] = None) -> EncryptionKey:
        """Generate new encryption key"""
        try:
            key_id = str(uuid.uuid4())
            
            if encryption_type == EncryptionType.AES_256_GCM:
                key_material = secrets.token_bytes(32)  # 256-bit key
                key_type = KeyType.SYMMETRIC
                algorithm = "AES"
                key_size = 256
                
            elif encryption_type == EncryptionType.AES_256_CBC:
                key_material = secrets.token_bytes(32)
                key_type = KeyType.SYMMETRIC
                algorithm = "AES"
                key_size = 256
                
            elif encryption_type == EncryptionType.FERNET:
                key_material = Fernet.generate_key()
                key_type = KeyType.SYMMETRIC
                algorithm = "Fernet"
                key_size = 256
                
            elif encryption_type == EncryptionType.RSA_2048:
                private_key = rsa.generate_private_key(
                    public_exponent=65537,
                    key_size=2048
                )
                key_material = private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                )
                public_key = private_key.public_key().public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo
                )
                key_type = KeyType.ASYMMETRIC_PRIVATE
                algorithm = "RSA"
                key_size = 2048
                
            elif encryption_type == EncryptionType.RSA_4096:
                private_key = rsa.generate_private_key(
                    public_exponent=65537,
                    key_size=4096
                )
                key_material = private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                )
                public_key = private_key.public_key().public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo
                )
                key_type = KeyType.ASYMMETRIC_PRIVATE
                algorithm = "RSA"
                key_size = 4096
                
            elif encryption_type == EncryptionType.CHACHA20_POLY1305:
                key_material = secrets.token_bytes(32)
                key_type = KeyType.SYMMETRIC
                algorithm = "ChaCha20-Poly1305"
                key_size = 256
                
            else:
                raise ValueError(f"Unsupported encryption type: {encryption_type}")
            
            # Encrypt key material with master key
            encrypted_key_material = self._encrypt_key_material(key_material)
            
            # Set expiration
            expires_at = None
            if expires_in_days:
                expires_at = datetime.utcnow() + timedelta(days=expires_in_days)
            
            key = EncryptionKey(
                key_id=key_id,
                key_type=key_type,
                encryption_type=encryption_type,
                status=KeyStatus.ACTIVE,
                created_at=datetime.utcnow(),
                expires_at=expires_at,
                key_material=encrypted_key_material,
                public_key=public_key if 'public_key' in locals() else None,
                algorithm=algorithm,
                key_size=key_size,
                usage=usage
            )
            
            self.keys[key_id] = key
            
            self.logger.info(f"Generated {encryption_type.value} key: {key_id}")
            return key
            
        except Exception as e:
            self.logger.error(f"Key generation failed: {e}")
            raise
    
    def _encrypt_key_material(self, key_material: bytes) -> bytes:
        """Encrypt key material with master key"""
        try:
            # Use Fernet for key material encryption
            fernet = Fernet(base64.urlsafe_b64encode(self.master_key))
            return fernet.encrypt(key_material)
            
        except Exception as e:
            self.logger.error(f"Key material encryption failed: {e}")
            raise
    
    def _decrypt_key_material(self, encrypted_key_material: bytes) -> bytes:
        """Decrypt key material with master key"""
        try:
            fernet = Fernet(base64.urlsafe_b64encode(self.master_key))
            return fernet.decrypt(encrypted_key_material)
            
        except Exception as e:
            self.logger.error(f"Key material decryption failed: {e}")
            raise
    
    async def get_key(self, key_id: str) -> Optional[EncryptionKey]:
        """Get encryption key by ID"""
        try:
            key = self.keys.get(key_id)
            
            if key and key.status == KeyStatus.ACTIVE:
                # Check expiration
                if key.expires_at and datetime.utcnow() > key.expires_at:
                    key.status = KeyStatus.EXPIRED
                    self.logger.warning(f"Key expired: {key_id}")
                    return None
                
                return key
            
            return None
            
        except Exception as e:
            self.logger.error(f"Key retrieval failed: {e}")
            return None
    
    async def revoke_key(self, key_id: str, reason: str = "") -> bool:
        """Revoke encryption key"""
        try:
            key = self.keys.get(key_id)
            if not key:
                return False
            
            key.status = KeyStatus.REVOKED
            key.metadata["revocation_reason"] = reason
            key.metadata["revoked_at"] = datetime.utcnow().isoformat()
            
            self.logger.info(f"Key revoked: {key_id} - {reason}")
            return True
            
        except Exception as e:
            self.logger.error(f"Key revocation failed: {e}")
            return False
    
    async def rotate_key(self, old_key_id: str) -> Optional[EncryptionKey]:
        """Rotate encryption key"""
        try:
            old_key = self.keys.get(old_key_id)
            if not old_key:
                return None
            
            # Generate new key with same parameters
            new_key = await self.generate_key(
                old_key.encryption_type,
                old_key.usage,
                expires_in_days=365  # Default 1 year expiration
            )
            
            # Mark old key as inactive
            old_key.status = KeyStatus.INACTIVE
            old_key.metadata["rotated_to"] = new_key.key_id
            old_key.metadata["rotated_at"] = datetime.utcnow().isoformat()
            
            # Link new key to old key
            new_key.metadata["rotated_from"] = old_key_id
            
            self.logger.info(f"Key rotated: {old_key_id} -> {new_key.key_id}")
            return new_key
            
        except Exception as e:
            self.logger.error(f"Key rotation failed: {e}")
            return None
    
    async def derive_key(self, password: str, salt: Optional[bytes] = None,
                        encryption_type: EncryptionType = EncryptionType.AES_256_GCM) -> EncryptionKey:
        """Derive key from password"""
        try:
            if not salt:
                salt = secrets.token_bytes(16)
            
            # Use Scrypt for key derivation
            kdf = Scrypt(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                n=2**14,
                r=8,
                p=1
            )
            
            key_material = kdf.derive(password.encode())
            
            # Encrypt derived key material
            encrypted_key_material = self._encrypt_key_material(key_material)
            
            key = EncryptionKey(
                key_id=str(uuid.uuid4()),
                key_type=KeyType.DERIVED,
                encryption_type=encryption_type,
                status=KeyStatus.ACTIVE,
                created_at=datetime.utcnow(),
                key_material=encrypted_key_material,
                algorithm="Scrypt-derived",
                key_size=256,
                usage=["encrypt", "decrypt"],
                metadata={"salt": base64.b64encode(salt).decode()}
            )
            
            self.keys[key.key_id] = key
            
            self.logger.info(f"Derived key from password: {key.key_id}")
            return key
            
        except Exception as e:
            self.logger.error(f"Key derivation failed: {e}")
            raise


class EncryptionService:
    """Comprehensive encryption service"""
    
    def __init__(self, master_key: Optional[bytes] = None):
        self.key_manager = KeyManager(master_key)
        self.operations: List[EncryptionOperation] = []
        
        # Encryption metrics
        self.metrics = {
            "operations_total": 0,
            "operations_successful": 0,
            "operations_failed": 0,
            "data_encrypted_bytes": 0,
            "data_decrypted_bytes": 0,
            "keys_generated": 0,
            "keys_rotated": 0
        }
        
        self.logger = logging.getLogger(__name__)
    
    async def initialize(self):
        """Initialize encryption service"""
        try:
            self.logger.info("Initializing Encryption Service...")
            
            # Generate default keys if none exist
            if not self.key_manager.keys:
                await self._generate_default_keys()
            
            self.logger.info("Encryption Service initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Encryption Service: {e}")
            raise
    
    async def _generate_default_keys(self):
        """Generate default encryption keys"""
        try:
            # Generate default AES key for general encryption
            await self.key_manager.generate_key(
                EncryptionType.AES_256_GCM,
                ["encrypt", "decrypt"],
                expires_in_days=365
            )
            
            # Generate RSA key pair for asymmetric operations
            await self.key_manager.generate_key(
                EncryptionType.RSA_2048,
                ["encrypt", "decrypt", "sign", "verify"],
                expires_in_days=730  # 2 years for RSA keys
            )
            
            self.logger.info("Default encryption keys generated")
            
        except Exception as e:
            self.logger.error(f"Default key generation failed: {e}")
    
    # Symmetric encryption
    async def encrypt_data(self, data: bytes, key_id: Optional[str] = None,
                          encryption_type: EncryptionType = EncryptionType.AES_256_GCM) -> Optional[EncryptedData]:
        """Encrypt data with symmetric encryption"""
        try:
            operation_id = str(uuid.uuid4())
            
            # Get or generate key
            if key_id:
                key = await self.key_manager.get_key(key_id)
                if not key:
                    raise ValueError(f"Key not found: {key_id}")
            else:
                # Find suitable key or generate new one
                key = await self._find_suitable_key(encryption_type, ["encrypt"])
                if not key:
                    key = await self.key_manager.generate_key(
                        encryption_type, ["encrypt", "decrypt"]
                    )
            
            # Decrypt key material
            key_material = self.key_manager._decrypt_key_material(key.key_material)
            
            # Perform encryption based on type
            if encryption_type == EncryptionType.AES_256_GCM:
                encrypted_data, iv, tag = await self._encrypt_aes_gcm(data, key_material)
                
                result = EncryptedData(
                    data_id=str(uuid.uuid4()),
                    encrypted_data=encrypted_data,
                    encryption_type=encryption_type,
                    key_id=key.key_id,
                    iv=iv,
                    tag=tag
                )
                
            elif encryption_type == EncryptionType.AES_256_CBC:
                encrypted_data, iv = await self._encrypt_aes_cbc(data, key_material)
                
                result = EncryptedData(
                    data_id=str(uuid.uuid4()),
                    encrypted_data=encrypted_data,
                    encryption_type=encryption_type,
                    key_id=key.key_id,
                    iv=iv
                )
                
            elif encryption_type == EncryptionType.FERNET:
                fernet = Fernet(key_material)
                encrypted_data = fernet.encrypt(data)
                
                result = EncryptedData(
                    data_id=str(uuid.uuid4()),
                    encrypted_data=encrypted_data,
                    encryption_type=encryption_type,
                    key_id=key.key_id
                )
                
            elif encryption_type == EncryptionType.CHACHA20_POLY1305:
                encrypted_data, nonce, tag = await self._encrypt_chacha20_poly1305(data, key_material)
                
                result = EncryptedData(
                    data_id=str(uuid.uuid4()),
                    encrypted_data=encrypted_data,
                    encryption_type=encryption_type,
                    key_id=key.key_id,
                    iv=nonce,
                    tag=tag
                )
                
            else:
                raise ValueError(f"Unsupported encryption type: {encryption_type}")
            
            # Record operation
            operation = EncryptionOperation(
                operation_id=operation_id,
                operation_type="encrypt",
                key_id=key.key_id,
                encryption_type=encryption_type,
                timestamp=datetime.utcnow(),
                data_size=len(data),
                success=True
            )
            
            self.operations.append(operation)
            self.metrics["operations_total"] += 1
            self.metrics["operations_successful"] += 1
            self.metrics["data_encrypted_bytes"] += len(data)
            
            self.logger.info(f"Data encrypted: {len(data)} bytes with {encryption_type.value}")
            return result
            
        except Exception as e:
            # Record failed operation
            operation = EncryptionOperation(
                operation_id=operation_id,
                operation_type="encrypt",
                key_id=key_id or "",
                encryption_type=encryption_type,
                timestamp=datetime.utcnow(),
                data_size=len(data) if data else 0,
                success=False,
                error_message=str(e)
            )
            
            self.operations.append(operation)
            self.metrics["operations_total"] += 1
            self.metrics["operations_failed"] += 1
            
            self.logger.error(f"Data encryption failed: {e}")
            return None
    
    async def decrypt_data(self, encrypted_data: EncryptedData) -> Optional[bytes]:
        """Decrypt data"""
        try:
            operation_id = str(uuid.uuid4())
            
            # Get key
            key = await self.key_manager.get_key(encrypted_data.key_id)
            if not key:
                raise ValueError(f"Key not found: {encrypted_data.key_id}")
            
            # Decrypt key material
            key_material = self.key_manager._decrypt_key_material(key.key_material)
            
            # Perform decryption based on type
            if encrypted_data.encryption_type == EncryptionType.AES_256_GCM:
                if not encrypted_data.iv or not encrypted_data.tag:
                    raise ValueError("IV and tag required for AES-GCM decryption")
                
                decrypted_data = await self._decrypt_aes_gcm(
                    encrypted_data.encrypted_data, key_material, 
                    encrypted_data.iv, encrypted_data.tag
                )
                
            elif encrypted_data.encryption_type == EncryptionType.AES_256_CBC:
                if not encrypted_data.iv:
                    raise ValueError("IV required for AES-CBC decryption")
                
                decrypted_data = await self._decrypt_aes_cbc(
                    encrypted_data.encrypted_data, key_material, encrypted_data.iv
                )
                
            elif encrypted_data.encryption_type == EncryptionType.FERNET:
                fernet = Fernet(key_material)
                decrypted_data = fernet.decrypt(encrypted_data.encrypted_data)
                
            elif encrypted_data.encryption_type == EncryptionType.CHACHA20_POLY1305:
                if not encrypted_data.iv or not encrypted_data.tag:
                    raise ValueError("Nonce and tag required for ChaCha20-Poly1305 decryption")
                
                decrypted_data = await self._decrypt_chacha20_poly1305(
                    encrypted_data.encrypted_data, key_material,
                    encrypted_data.iv, encrypted_data.tag
                )
                
            else:
                raise ValueError(f"Unsupported encryption type: {encrypted_data.encryption_type}")
            
            # Record operation
            operation = EncryptionOperation(
                operation_id=operation_id,
                operation_type="decrypt",
                key_id=encrypted_data.key_id,
                encryption_type=encrypted_data.encryption_type,
                timestamp=datetime.utcnow(),
                data_size=len(decrypted_data),
                success=True
            )
            
            self.operations.append(operation)
            self.metrics["operations_total"] += 1
            self.metrics["operations_successful"] += 1
            self.metrics["data_decrypted_bytes"] += len(decrypted_data)
            
            self.logger.info(f"Data decrypted: {len(decrypted_data)} bytes")
            return decrypted_data
            
        except Exception as e:
            # Record failed operation
            operation = EncryptionOperation(
                operation_id=operation_id,
                operation_type="decrypt",
                key_id=encrypted_data.key_id,
                encryption_type=encrypted_data.encryption_type,
                timestamp=datetime.utcnow(),
                data_size=0,
                success=False,
                error_message=str(e)
            )
            
            self.operations.append(operation)
            self.metrics["operations_total"] += 1
            self.metrics["operations_failed"] += 1
            
            self.logger.error(f"Data decryption failed: {e}")
            return None
    
    # Encryption algorithm implementations
    async def _encrypt_aes_gcm(self, data: bytes, key: bytes) -> Tuple[bytes, bytes, bytes]:
        """Encrypt with AES-256-GCM"""
        iv = secrets.token_bytes(12)  # 96-bit IV for GCM
        
        cipher = Cipher(
            algorithms.AES(key),
            modes.GCM(iv)
        )
        
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(data) + encryptor.finalize()
        
        return ciphertext, iv, encryptor.tag
    
    async def _decrypt_aes_gcm(self, ciphertext: bytes, key: bytes, 
                              iv: bytes, tag: bytes) -> bytes:
        """Decrypt with AES-256-GCM"""
        cipher = Cipher(
            algorithms.AES(key),
            modes.GCM(iv, tag)
        )
        
        decryptor = cipher.decryptor()
        plaintext = decryptor.update(ciphertext) + decryptor.finalize()
        
        return plaintext
    
    async def _encrypt_aes_cbc(self, data: bytes, key: bytes) -> Tuple[bytes, bytes]:
        """Encrypt with AES-256-CBC"""
        # Pad data to block size
        block_size = 16
        padding_length = block_size - (len(data) % block_size)
        padded_data = data + bytes([padding_length] * padding_length)
        
        iv = secrets.token_bytes(16)  # 128-bit IV
        
        cipher = Cipher(
            algorithms.AES(key),
            modes.CBC(iv)
        )
        
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(padded_data) + encryptor.finalize()
        
        return ciphertext, iv
    
    async def _decrypt_aes_cbc(self, ciphertext: bytes, key: bytes, iv: bytes) -> bytes:
        """Decrypt with AES-256-CBC"""
        cipher = Cipher(
            algorithms.AES(key),
            modes.CBC(iv)
        )
        
        decryptor = cipher.decryptor()
        padded_data = decryptor.update(ciphertext) + decryptor.finalize()
        
        # Remove padding
        padding_length = padded_data[-1]
        plaintext = padded_data[:-padding_length]
        
        return plaintext
    
    async def _encrypt_chacha20_poly1305(self, data: bytes, key: bytes) -> Tuple[bytes, bytes, bytes]:
        """Encrypt with ChaCha20-Poly1305"""
        nonce = secrets.token_bytes(12)  # 96-bit nonce
        
        cipher = Cipher(
            algorithms.ChaCha20(key, nonce),
            modes.GCM(nonce)
        )
        
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(data) + encryptor.finalize()
        
        return ciphertext, nonce, encryptor.tag
    
    async def _decrypt_chacha20_poly1305(self, ciphertext: bytes, key: bytes,
                                       nonce: bytes, tag: bytes) -> bytes:
        """Decrypt with ChaCha20-Poly1305"""
        cipher = Cipher(
            algorithms.ChaCha20(key, nonce),
            modes.GCM(nonce, tag)
        )
        
        decryptor = cipher.decryptor()
        plaintext = decryptor.update(ciphertext) + decryptor.finalize()
        
        return plaintext
    
    # Asymmetric encryption
    async def encrypt_with_public_key(self, data: bytes, key_id: str) -> Optional[bytes]:
        """Encrypt data with RSA public key"""
        try:
            key = await self.key_manager.get_key(key_id)
            if not key or not key.public_key:
                raise ValueError(f"Public key not found: {key_id}")
            
            # Load public key
            public_key = serialization.load_pem_public_key(key.public_key)
            
            # Encrypt with OAEP padding
            ciphertext = public_key.encrypt(
                data,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            
            self.logger.info(f"Data encrypted with public key: {key_id}")
            return ciphertext
            
        except Exception as e:
            self.logger.error(f"Public key encryption failed: {e}")
            return None
    
    async def decrypt_with_private_key(self, ciphertext: bytes, key_id: str) -> Optional[bytes]:
        """Decrypt data with RSA private key"""
        try:
            key = await self.key_manager.get_key(key_id)
            if not key or not key.key_material:
                raise ValueError(f"Private key not found: {key_id}")
            
            # Decrypt key material and load private key
            key_material = self.key_manager._decrypt_key_material(key.key_material)
            private_key = serialization.load_pem_private_key(key_material, password=None)
            
            # Decrypt with OAEP padding
            plaintext = private_key.decrypt(
                ciphertext,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            
            self.logger.info(f"Data decrypted with private key: {key_id}")
            return plaintext
            
        except Exception as e:
            self.logger.error(f"Private key decryption failed: {e}")
            return None
    
    # Utility methods
    async def _find_suitable_key(self, encryption_type: EncryptionType, 
                               usage: List[str]) -> Optional[EncryptionKey]:
        """Find suitable key for operation"""
        for key in self.key_manager.keys.values():
            if (key.encryption_type == encryption_type and
                key.status == KeyStatus.ACTIVE and
                all(u in key.usage for u in usage)):
                return key
        return None
    
    async def hash_data(self, data: bytes, algorithm: str = "sha256") -> bytes:
        """Hash data with specified algorithm"""
        try:
            if algorithm == "sha256":
                digest = hashes.Hash(hashes.SHA256())
            elif algorithm == "sha512":
                digest = hashes.Hash(hashes.SHA512())
            elif algorithm == "sha1":
                digest = hashes.Hash(hashes.SHA1())
            else:
                raise ValueError(f"Unsupported hash algorithm: {algorithm}")
            
            digest.update(data)
            return digest.finalize()
            
        except Exception as e:
            self.logger.error(f"Data hashing failed: {e}")
            raise
    
    async def generate_random_bytes(self, length: int) -> bytes:
        """Generate cryptographically secure random bytes"""
        return secrets.token_bytes(length)
    
    # Key management operations
    async def generate_key(self, encryption_type: EncryptionType,
                          usage: List[str], expires_in_days: Optional[int] = None) -> Optional[EncryptionKey]:
        """Generate new encryption key"""
        try:
            key = await self.key_manager.generate_key(encryption_type, usage, expires_in_days)
            self.metrics["keys_generated"] += 1
            return key
            
        except Exception as e:
            self.logger.error(f"Key generation failed: {e}")
            return None
    
    async def rotate_key(self, key_id: str) -> Optional[EncryptionKey]:
        """Rotate encryption key"""
        try:
            new_key = await self.key_manager.rotate_key(key_id)
            if new_key:
                self.metrics["keys_rotated"] += 1
            return new_key
            
        except Exception as e:
            self.logger.error(f"Key rotation failed: {e}")
            return None
    
    async def get_encryption_metrics(self) -> Dict[str, Any]:
        """Get encryption service metrics"""
        try:
            now = datetime.utcnow()
            
            # Key statistics
            active_keys = len([k for k in self.key_manager.keys.values() 
                             if k.status == KeyStatus.ACTIVE])
            
            key_type_distribution = {}
            for key_type in KeyType:
                count = len([k for k in self.key_manager.keys.values() 
                           if k.key_type == key_type])
                key_type_distribution[key_type.value] = count
            
            encryption_type_distribution = {}
            for enc_type in EncryptionType:
                count = len([k for k in self.key_manager.keys.values() 
                           if k.encryption_type == enc_type])
                encryption_type_distribution[enc_type.value] = count
            
            # Recent operations
            recent_operations = [op for op in self.operations 
                               if op.timestamp > now - timedelta(hours=24)]
            
            return {
                "keys": {
                    "total": len(self.key_manager.keys),
                    "active": active_keys,
                    "type_distribution": key_type_distribution,
                    "encryption_type_distribution": encryption_type_distribution
                },
                "operations": {
                    "total": len(self.operations),
                    "recent_24h": len(recent_operations),
                    "success_rate": (self.metrics["operations_successful"] / 
                                   self.metrics["operations_total"]) if self.metrics["operations_total"] > 0 else 0
                },
                "metrics": self.metrics,
                "metrics_timestamp": now.isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get encryption metrics: {e}")
            return {}