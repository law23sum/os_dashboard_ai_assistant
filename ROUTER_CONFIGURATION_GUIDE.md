# Router Security & Performance Configuration Guide
## Frontier NVG468MQ Router Optimization

Based on your router status page, here are recommended configurations to maximize security and performance while maintaining excellent internet speed and low latency.

---

## 🔐 SECURITY CONFIGURATIONS

### 1. **Change Default Router Admin Password** ⚠️ CRITICAL
- **Location**: Main → Admin → Password Settings
- **Action**: Change default admin password to strong unique password (16+ characters, mix of letters, numbers, symbols)
- **Impact**: Prevents unauthorized router access
- **Performance Impact**: None

### 2. **Enable WPA3 or Use Strong WPA2-AES** 
- **Location**: Wireless → Security Settings
- **Current**: WPA2 (acceptable but outdated)
- **Recommended**: 
  - If available: Enable **WPA3** (most secure)
  - If WPA3 not available: Use **WPA2-PSK (AES only)** - disable TKIP
- **Action**: 
  1. Go to Wireless → Security
  2. Set encryption to WPA3-Personal (or WPA2-PSK if WPA3 unavailable)
  3. Ensure AES is enabled (disable TKIP if present)
  4. Set strong WiFi password (20+ characters, random)
- **Impact**: Significantly improves security
- **Performance Impact**: Minimal (AES is hardware-accelerated)

### 3. **Disable WPS (Wi-Fi Protected Setup)** ⚠️ CRITICAL
- **Location**: Wireless → WPS Settings
- **Action**: Disable WPS completely
- **Impact**: Prevents brute-force attacks on WPS PIN
- **Performance Impact**: None (WPS only used during initial setup)

### 4. **Change Default SSID Names**
- **Location**: Wireless → Basic Settings
- **Current**: Frontier3216, Frontier_5G
- **Action**: 
  - Change to non-identifying names (don't use personal info)
  - Example: `HomeNet-5G`, `MainNetwork-2.4`
- **Impact**: Prevents router identification by attackers
- **Performance Impact**: None

### 5. **Hide SSID Broadcast (Optional - Advanced)**
- **Location**: Wireless → Basic Settings → SSID Broadcast
- **Action**: Disable SSID broadcast for additional obscurity
- **Impact**: Reduces visibility but not real security (can still be detected)
- **Performance Impact**: Slight initial connection delay
- **Note**: Only use if you don't mind manually entering SSID on new devices

### 6. **Enable MAC Address Filtering** 🔒 RECOMMENDED
- **Location**: Wireless → MAC Filtering (or Firewall → Access Control)
- **Action**: 
  1. Enable MAC address filtering
  2. Set to "Allow List" mode
  3. Add MAC addresses of ALL trusted devices
  4. **Block the suspicious device**: Add `laptop-0onevps8` to block list if still unknown
- **Impact**: Prevents unauthorized devices from connecting
- **Performance Impact**: None
- **Note**: Find MAC addresses: On Mac `ifconfig`, on Windows `ipconfig /all`

### 7. **Disable Remote Management**
- **Location**: Advanced → Remote Management
- **Action**: Disable remote WAN access to router admin
- **Impact**: Prevents external access to router configuration
- **Performance Impact**: None

### 8. **Update Firmware** ⚠️ IMPORTANT
- **Location**: Advanced → Firmware Update or Status → Tech Support
- **Current**: 9.3.0h7d91
- **Action**: 
  1. Check Frontier's website for latest firmware
  2. Or use router's auto-update feature if available
  3. Schedule updates during maintenance window
- **Impact**: Fixes security vulnerabilities and performance bugs
- **Performance Impact**: May improve stability and speed

### 9. **Enable Firewall & Configure Properly**
- **Location**: Firewall → Settings
- **Action**: 
  - Ensure firewall is **Enabled**
  - Set to "Maximum" or "High" security level
  - Enable SPI (Stateful Packet Inspection)
  - Enable DoS protection
- **Impact**: Blocks malicious traffic
- **Performance Impact**: Minimal (modern routers handle this efficiently)

### 10. **Disable UPnP (Universal Plug and Play)** 🔒 RECOMMENDED
- **Location**: Status → UPnP or Advanced → UPnP
- **Action**: Disable UPnP
- **Impact**: Prevents malicious apps from opening ports automatically
- **Performance Impact**: None (you'll need to manually port-forward if needed)
- **Alternative**: If you need UPnP for gaming/streaming, enable but monitor closely

### 11. **Change Default DNS Servers** 🚀 PERFORMANCE + SECURITY
- **Location**: Network → DHCP or Advanced → DNS
- **Current**: 74.40.74.40, 74.40.74.41 (Frontier DNS)
- **Recommended Options**:
  
  **Option A - Best Performance & Privacy:**
  - Primary: `1.1.1.1` (Cloudflare)
  - Secondary: `1.0.0.1` (Cloudflare)
  
  **Option B - Privacy Focused:**
  - Primary: `1.1.1.2` (Cloudflare with malware blocking)
  - Secondary: `1.0.0.2` (Cloudflare with malware blocking)
  
  **Option C - Google (Fast but privacy concerns):**
  - Primary: `8.8.8.8`
  - Secondary: `8.8.4.4`
  
  **Option D - Quad9 (Security focused):**
  - Primary: `9.9.9.9`
  - Secondary: `149.112.112.112`

- **Action**: 
  1. Go to Network → DHCP Settings
  2. Set "DNS Server 1" to your chosen primary
  3. Set "DNS Server 2" to your chosen secondary
  4. Save and restart router
- **Impact**: 
  - Faster DNS resolution (lower latency)
  - Better privacy (Cloudflare doesn't log)
  - Malware blocking (if using filtered DNS)
- **Performance Impact**: **IMPROVES latency** - typically 10-30ms faster DNS lookups

### 12. **Enable Guest Network (If Available)**
- **Location**: Wireless → Guest Network
- **Action**: 
  - Enable separate guest network
  - Use different password
  - Enable client isolation (devices can't see each other)
  - Set bandwidth limits if available
- **Impact**: Isolates guest devices from your main network
- **Performance Impact**: None (may actually improve main network performance)

### 13. **Review and Limit Port Forwarding**
- **Location**: Firewall → Port Forwarding or Advanced → NAT
- **Action**: 
  - Review all port forwarding rules
  - Remove any unnecessary rules
  - Only forward ports you actively use
- **Impact**: Reduces attack surface
- **Performance Impact**: None

---

## ⚡ PERFORMANCE OPTIMIZATIONS

### 14. **Optimize Wireless Channel Selection** 🚀 RECOMMENDED
- **Location**: Wireless → Advanced → Channel Settings
- **Current**: Auto (likely causing interference)
- **Action**:
  1. Download WiFi analyzer app on phone (e.g., WiFi Explorer, NetSpot)
  2. Check which channels are least crowded
  3. For 5GHz: Use channels 36, 40, 44, 48, 149, 153, 157, 161, 165
     - Avoid DFS channels (50-144) if not needed
     - Use 80MHz or 160MHz width for maximum speed
  4. For 2.4GHz: Use channels 1, 6, or 11 (non-overlapping)
  5. Set manually in router settings
- **Impact**: Reduces interference, improves speed and stability
- **Performance Impact**: **SIGNIFICANT** - can improve speeds 20-50%

### 15. **Enable Band Steering (If Available)**
- **Location**: Wireless → Advanced → Band Steering
- **Action**: Enable automatic 5GHz preference for capable devices
- **Impact**: Keeps fast devices on 5GHz, slower devices on 2.4GHz
- **Performance Impact**: **IMPROVES** - better overall network efficiency

### 16. **Enable QoS (Quality of Service)** 🚀 RECOMMENDED
- **Location**: Advanced → QoS or Traffic Management
- **Action**: 
  1. Enable QoS
  2. Set your connection speed: 1000 Mbps (based on your 1000/Full link)
  3. Configure priority rules:
     - High priority: Gaming, Video Streaming, VoIP
     - Medium: Web browsing
     - Low: Downloads, backups
  4. Or enable automatic QoS if available
- **Impact**: Prevents one device from hogging bandwidth
- **Performance Impact**: **IMPROVES** - smoother performance during heavy usage

### 17. **Optimize Transmit Power**
- **Location**: Wireless → Advanced → Transmit Power
- **Action**: 
  - Set to "High" or "100%" for better coverage
  - Or use "Auto" if available
  - Avoid "Maximum" (can cause interference)
- **Impact**: Better signal strength and range
- **Performance Impact**: **IMPROVES** - especially at distance

### 18. **Enable IPv6 (If Your ISP Supports It)**
- **Location**: Network → IPv6 Settings
- **Action**: 
  1. Check with Frontier if IPv6 is available
  2. If yes, enable IPv6 with auto-configuration
  3. Use DHCPv6 or SLAAC
- **Impact**: Future-proofs network, may improve performance
- **Performance Impact**: **Slight improvement** for IPv6-enabled sites

### 19. **Disable Unnecessary Features** 🚀 RECOMMENDED
- **Location**: Various
- **Actions**:
  - Disable "Wireless Controller" (currently disabled - good)
  - Disable MoCA if not using cable networking
  - Disable Voice features if not using VoIP
  - Disable unused USB sharing features
- **Impact**: Reduces CPU load, improves stability
- **Performance Impact**: **Slight improvement** - frees router resources

### 20. **Adjust MTU Size (Advanced)**
- **Location**: Network → WAN Settings → MTU
- **Current**: Likely 1500 (default)
- **Action**: 
  - Test optimal MTU: `ping -D -s 1472 8.8.8.8` (increase until packets fragment)
  - Set to largest value that doesn't fragment minus 28
  - Typically 1492 for PPPoE, 1500 for direct connections
- **Impact**: Optimizes packet size for your connection
- **Performance Impact**: **Minor improvement** - 1-2% in some cases

---

## 🔍 MONITORING & MAINTENANCE

### 21. **Block Suspicious Device: laptop-0onevps8** ⚠️ IMMEDIATE ACTION
- **Location**: Firewall → Access Control or Status → ARP Table
- **Action**: 
  1. Go to Status → ARP Table
  2. Find entries with IPs: 192.168.254.154 or 192.168.254.192
  3. Note the MAC address (if complete)
  4. Go to Firewall → Access Control
  5. Add MAC address to blocked list
  6. Or use MAC Filtering to explicitly deny
- **Impact**: Prevents suspicious device from accessing network
- **Performance Impact**: None (may actually improve security posture)

### 22. **Enable Router Logging**
- **Location**: Status → Logs or Advanced → Logging
- **Action**: 
  - Enable logging
  - Set log level to "Informational" or "Warning"
  - Enable email/SMS alerts if available
- **Impact**: Helps detect suspicious activity
- **Performance Impact**: Minimal

### 23. **Regular Security Audits**
- **Schedule**: Monthly
- **Actions**:
  - Review connected devices list
  - Check for firmware updates
  - Review firewall logs
  - Verify MAC filtering list is current
  - Check for unknown devices

---

## 🔄 TWO-ROUTER CONFIGURATION SETUP

Based on your network, here are the best two-router configurations:

### **Option 1: Router-in-AP Mode (RECOMMENDED for Performance)** ⭐

**Best for**: Maximum performance, single network, seamless roaming

**Setup**:
1. **Primary Router (Frontier NVG468MQ)**: Keep as main router
   - Handles DHCP, routing, firewall
   - Connect to ONT/Internet
   - Use 5GHz network (Frontier_5G)

2. **Secondary Router**: Configure as Access Point (AP) mode
   - **Location**: Advanced → Operation Mode → Access Point Mode
   - **If AP mode unavailable**, manually configure:
     - Disable DHCP server on secondary router
     - Set LAN IP to 192.168.254.2 (outside primary DHCP range)
     - Connect secondary router's LAN port to primary router's LAN port
     - **DO NOT** use WAN port on secondary router
     - Configure same SSID but different channel:
       - Primary: Frontier_5G on channel 36
       - Secondary: Frontier_5G on channel 149
     - Use same WiFi password and security settings
   - Use 2.4GHz or different 5GHz channel for coverage
   - Place in area with weak signal from primary

**Benefits**:
- ✅ Single network name (seamless roaming)
- ✅ Maximum performance (no double NAT)
- ✅ Simple device management
- ✅ Better coverage

**Performance**: **OPTIMAL** - No performance penalty

---

### **Option 2: Cascaded Routers (Alternative)**

**Best for**: Network isolation, guest network separation

**Setup**:
1. **Primary Router (Frontier)**: Main router
   - Connect to Internet
   - DHCP range: 192.168.254.2-192.168.254.127

2. **Secondary Router**: Subnet router
   - Connect WAN port to primary router LAN port
   - Set WAN IP: DHCP (gets IP from primary)
   - Set LAN IP: 192.168.1.1 (different subnet)
   - DHCP range: 192.168.1.2-192.168.1.254
   - Use different SSID

**Benefits**:
- ✅ Network isolation
- ✅ Separate guest network
- ✅ Extra security layer

**Drawbacks**:
- ⚠️ Double NAT (slight latency increase)
- ⚠️ Port forwarding more complex
- ⚠️ Devices on different networks can't easily communicate

**Performance**: **GOOD** - Slight latency penalty (~1-2ms)

---

### **Option 3: Mesh Network (If Compatible Routers)**

**Best for**: Large homes, seamless coverage

**Setup**:
- Use routers with mesh capabilities
- Configure mesh network
- Automatic channel optimization
- Seamless handoff between nodes

**Performance**: **EXCELLENT** - Optimized automatically

---

## 📊 PRIORITY IMPLEMENTATION ORDER

### **Immediate (Do Today)**:
1. Change admin password (#1)
2. Block suspicious device laptop-0onevps8 (#21)
3. Enable MAC filtering (#6)
4. Disable WPS (#3)
5. Change DNS servers (#11) - **Quick performance win**

### **This Week**:
6. Update firmware (#8)
7. Optimize wireless channels (#14) - **Big performance win**
8. Enable QoS (#16) - **Performance improvement**
9. Enable firewall properly (#9)
10. Disable UPnP (#10)

### **This Month**:
11. Upgrade to WPA3 (#2)
12. Configure two-router setup (choose option above)
13. Set up guest network (#12)
14. Review port forwarding (#13)
15. Enable logging (#22)

---

## 📈 EXPECTED PERFORMANCE IMPROVEMENTS

After implementing these changes:
- **Latency**: 10-30ms improvement (from DNS optimization)
- **WiFi Speed**: 20-50% improvement (from channel optimization)
- **Network Stability**: Significant improvement (from proper configuration)
- **Security Posture**: Major improvement (from layered security)

---

## 🔧 TROUBLESHOOTING

### If Internet becomes slow after changes:
1. Revert DNS changes first (may need ISP DNS)
2. Check QoS settings (may be throttling)
3. Verify channel selection (may have chosen bad channel)
4. Check firewall isn't blocking legitimate traffic

### If devices can't connect:
1. Verify MAC filtering list includes all devices
2. Check WiFi password is correct
3. Verify SSID hasn't changed
4. Check if device supports WPA3 (may need WPA2)

### If suspicious device reappears:
1. Check router logs for connection time
2. Verify MAC filtering is working
3. Consider changing WiFi password
4. Enable additional logging

---

## 📝 CONFIGURATION CHECKLIST

Print this and check off as you complete:

**Security**:
- [ ] Admin password changed
- [ ] WPA3/WPA2-AES enabled
- [ ] WPS disabled
- [ ] SSID names changed
- [ ] MAC filtering enabled
- [ ] Remote management disabled
- [ ] Firmware updated
- [ ] Firewall enabled & configured
- [ ] UPnP disabled
- [ ] DNS changed (Cloudflare recommended)
- [ ] Guest network configured
- [ ] Suspicious device blocked

**Performance**:
- [ ] Wireless channels optimized
- [ ] QoS enabled
- [ ] Transmit power optimized
- [ ] Unnecessary features disabled
- [ ] Two-router setup configured (if applicable)

**Monitoring**:
- [ ] Logging enabled
- [ ] Monthly audit scheduled

---

## 📞 SUPPORT

- **Frontier Support**: Check your router's Tech Support Info page
- **Router Manual**: Should be available on Frontier's website
- **Firmware Updates**: Check Frontier's customer portal

---

**Last Updated**: December 2025
**Router Model**: Frontier NVG468MQ
**Firmware**: 9.3.0h7d91





