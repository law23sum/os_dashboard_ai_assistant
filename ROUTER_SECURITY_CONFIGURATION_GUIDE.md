# Router Security Configuration Guide
## Frontier Communications NVG468MQ Router

**Router IP:** 192.168.254.254  
**Current Firmware:** 9.3.0h7d91  
**Date:** December 17, 2025

---

## 🔐 Authentication Required

To make configuration changes, you'll need to log in with:
- **Username:** admin
- **Password:** (Found on the side or bottom of your gateway/router)

---

## 📋 Security Configuration Checklist

### 1. FIREWALL SETTINGS (Priority: HIGH)

**Navigate to:** Firewall → Level

#### Firewall Level Configuration:
- [ ] **IPv4 Firewall Level:** Change from `Low` to `High`
  - High provides maximum protection by blocking all unsolicited inbound traffic
  - Only allows responses to outbound connections
  
- [ ] **IPv6 Firewall Level:** Change from `Low` to `High`
  - Ensures IPv6 traffic is also properly protected

**Why:** Low firewall settings allow more incoming connections, increasing attack surface. High settings provide better protection while maintaining functionality for legitimate traffic.

---

### 2. SERVICE BLOCKING (Priority: HIGH)

**Navigate to:** Firewall → Blocking

#### Enable Service Blocking:
- [ ] **Enable Service Blocking:** Change from `Disabled` to `Enabled`
- [ ] Configure which services to block:
  - Block unnecessary services (FTP, Telnet, etc.) if not in use
  - Keep essential services (HTTP, HTTPS) enabled only if needed
  - Consider blocking P2P services if not required

**Why:** Prevents unauthorized access to specific network services and reduces attack vectors.

---

### 3. WEBSITE BLOCKING (Priority: MEDIUM)

**Navigate to:** Firewall → Blocking (or separate Website Blocking section)

#### Enable Website Blocking:
- [ ] **Enable Website Blocking:** Change from `Disabled` to `Enabled`
- [ ] Configure blocking rules:
  - Add malicious domains/IPs to block list
  - Consider blocking known malware/phishing sites
  - Configure time-based blocking if needed

**Why:** Provides additional layer of protection against malicious websites and phishing attempts.

---

### 4. WIRELESS SECURITY (Priority: HIGH)

**Navigate to:** Wireless

#### 5 GHz Network (Currently Enabled):
- [ ] **Encryption:** Check if WPA3 is available, upgrade from WPA2 if possible
  - Current: WPA2
  - Preferred: WPA3 (if supported by router and devices)
  - If WPA3 not available, ensure WPA2 with AES encryption (not TKIP)

- [ ] **SSID Broadcast:** Consider hiding SSID (disable broadcast)
  - Navigate to Wireless → Advanced Settings
  - Enable "Hide SSID" or "Disable SSID Broadcast"
  - **Note:** You'll need to manually connect devices after this change

- [ ] **Change Default SSID:** Change from `Frontier_5G` to something unique
  - Avoid personal information in SSID name
  - Use a strong, unique name

- [ ] **Change Wi-Fi Password:** Ensure strong password
  - Minimum 12 characters
  - Mix of uppercase, lowercase, numbers, symbols
  - Avoid dictionary words

- [ ] **MAC Address Filtering:** Consider enabling
  - Only allow specific devices to connect
  - More secure but requires managing device list

#### 2.4 GHz Network (Currently Disabled):
- [x] **Keep Disabled** (if not needed)
  - Reduces attack surface
  - Only enable if you have devices that require 2.4 GHz

#### Guest Networks:
- [x] **Keep Guest SSIDs Disabled** (Current: Disabled)
  - Good security practice
  - Only enable if you need guest access, then:
    - Use separate, strong password
    - Enable client isolation
    - Set time limits if possible

---

### 5. NETWORK SETTINGS (Priority: MEDIUM)

**Navigate to:** Network

#### DHCP Settings:
- [ ] **Review DHCP Lease Time:** Set to reasonable value (24 hours recommended)
- [ ] **DHCP Address Pool:** Review and ensure appropriate range
  - Current LAN: 192.168.254.0/24
  - Ensure pool doesn't conflict with static IPs

#### Static IP Configuration:
- [ ] Review any static IP assignments
- [ ] Ensure only necessary devices have static IPs

---

### 6. ADVANCED SECURITY SETTINGS (Priority: MEDIUM)

**Navigate to:** Advanced

#### UPnP (Universal Plug and Play):
- [x] **Keep Disabled** (Current: Disabled) ✅
  - UPnP can create security vulnerabilities
  - Only enable if absolutely necessary for specific applications

#### Port Forwarding:
- [x] **Keep Disabled** (Current: Disabled) ✅
  - Only enable if you need to host services
  - If enabled, forward only necessary ports
  - Use specific IP addresses, not entire ranges

#### DMZ (Demilitarized Zone):
- [x] **Keep Disabled** (Current: Disabled) ✅
  - DMZ exposes devices directly to internet
  - Only use if absolutely necessary

#### DoS Protection:
- [ ] **Navigate to:** Firewall → DoS
- [ ] **Enable DoS Protection:** Ensure enabled
  - Protects against Denial of Service attacks
  - Configure thresholds appropriately

#### ALG Passthrough:
- [ ] **Review ALG Passthrough Settings:**
  - Current: Enabled
  - Review which protocols are allowed
  - Disable unnecessary ALG passthroughs (FTP, SIP, etc.) if not needed

---

### 7. ACCESS CONTROL (Priority: HIGH)

**Navigate to:** Firewall → Access Control

#### MAC Address Filtering:
- [ ] **Consider Enabling MAC Address Filtering:**
  - Whitelist only known devices
  - Prevents unauthorized devices from connecting
  - More secure but requires device management

#### Parental Controls / Time Restrictions:
- [ ] Configure if needed for your network
- [ ] Set appropriate time-based access rules

---

### 8. FIRMWARE & UPDATES (Priority: HIGH)

**Navigate to:** Advanced → System or Maintenance

#### Firmware Updates:
- [ ] **Check for Firmware Updates:**
  - Current: 9.3.0h7d91
  - Check Frontier's website for latest firmware
  - Update if newer version available
  - **Important:** Updates often include security patches

#### Automatic Updates:
- [ ] **Enable Automatic Updates** (if available)
  - Ensures you receive security patches automatically
  - Reduces risk of running outdated firmware

---

### 9. ADMINISTRATIVE SECURITY (Priority: HIGH)

**Navigate to:** Advanced → Administration or System

#### Admin Password:
- [ ] **Change Default Admin Password:**
  - Use strong, unique password
  - Store securely (password manager)
  - Never share with unauthorized users

#### Remote Management:
- [ ] **Disable Remote Management** (if enabled)
  - Prevents external access to router admin
  - Only enable if absolutely necessary
  - If enabled, use strong password and restrict IPs

#### HTTPS/SSL:
- [ ] **Enable HTTPS for Admin Interface** (if available)
  - Encrypts admin interface traffic
  - Prevents password interception

#### Admin Session Timeout:
- [ ] **Set Appropriate Session Timeout:**
  - Auto-logout after inactivity
  - Recommended: 15-30 minutes

---

### 10. LOGGING & MONITORING (Priority: MEDIUM)

**Navigate to:** Status → Logs

#### Enable Logging:
- [ ] **Enable Security Event Logging:**
  - Log firewall events
  - Log blocked connections
  - Log authentication attempts
  - Review logs regularly

#### Log Retention:
- [ ] **Configure Log Retention:**
  - Keep logs for reasonable period (30-90 days)
  - Regular review helps identify threats

---

### 11. DNS SECURITY (Priority: MEDIUM)

**Navigate to:** Network → DNS or Advanced → DNS

#### DNS Settings:
- [ ] **Consider Using Secure DNS:**
  - Current: 74.40.74.40, 74.40.74.41 (Frontier DNS)
  - Consider: Cloudflare (1.1.1.1, 1.0.0.1) or Google (8.8.8.8, 8.8.4.4)
  - Or use DNS over HTTPS (DoH) if supported

**Why:** Secure DNS can provide additional protection against malicious domains.

---

### 12. IPv6 SECURITY (Priority: LOW-MEDIUM)

**Current Status:** IPv6 Enabled

#### IPv6 Configuration:
- [ ] **Review IPv6 Firewall Rules:**
  - Ensure IPv6 firewall is set to High (see Firewall section)
  - Review IPv6 access rules
  - Consider disabling IPv6 if not needed (reduces attack surface)

---

## 🔄 Configuration Order (Recommended)

1. **First:** Change admin password
2. **Second:** Update firewall levels (IPv4 and IPv6) to High
3. **Third:** Enable service blocking and website blocking
4. **Fourth:** Configure wireless security (WPA3, hide SSID, change passwords)
5. **Fifth:** Review and configure DoS protection
6. **Sixth:** Check for firmware updates
7. **Seventh:** Configure logging
8. **Eighth:** Review advanced settings (ALG, access control)

---

## ✅ Current Good Security Practices (Already Configured)

- ✅ UPnP: Disabled
- ✅ Port Forwarding: Disabled  
- ✅ DMZ: Disabled
- ✅ Guest Networks: Disabled
- ✅ 2.4 GHz Radio: Disabled (reduces attack surface)
- ✅ NAT: Enabled
- ✅ Packet Filtering: Enabled

---

## ⚠️ Important Notes

1. **Backup Configuration:** Before making changes, backup your current router configuration (if option available in Advanced → Backup/Restore)

2. **Test After Changes:** After each major change, test your internet connectivity and ensure devices can still connect

3. **Document Changes:** Keep a record of changes made, especially:
   - New passwords
   - Static IP assignments
   - Port forwarding rules
   - MAC address filters

4. **Regular Reviews:** Review security settings quarterly or after security incidents

5. **Firmware Updates:** Check for firmware updates every 3-6 months

---

## 🚨 Security Best Practices Summary

- **Maximum Protection:** High firewall levels, service blocking enabled
- **Minimize Attack Surface:** Disable unused features (UPnP, DMZ, guest networks)
- **Strong Authentication:** WPA3/WPA2-AES, strong passwords, MAC filtering
- **Hidden Network:** Disable SSID broadcast (optional but more secure)
- **Regular Updates:** Keep firmware updated
- **Monitoring:** Enable logging and review regularly
- **Least Privilege:** Only enable features you actually need

---

## 📞 Support

If you encounter issues after making changes:
1. Check router logs (Status → Logs)
2. Try rebooting the router
3. Contact Frontier support if needed
4. Restore from backup if configuration backup was created

---

**Last Updated:** December 17, 2025  
**Router Model:** NVG468MQ  
**Firmware:** 9.3.0h7d91

