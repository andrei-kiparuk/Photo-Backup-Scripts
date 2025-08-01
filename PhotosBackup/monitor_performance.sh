#!/bin/bash

# Performance Monitoring Script
# Tracks system performance metrics for network and Photos operations

set -euo pipefail

# Set locale for proper Unicode/international character handling
export LC_ALL=en_US.UTF-8
export LANG=en_US.UTF-8

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1"
}

error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1"
}

# Performance monitoring function
monitor_performance() {
    echo "======================================"
    echo "    📊 Mac Performance Monitor"
    echo "======================================"
    echo "Timestamp: $(date)"
    echo ""
    
    # System Resources
    echo "💾 Memory Status:"
    echo "  $(vm_stat | awk '/Pages free/ {printf "  Free: %.1fGB", $3*4096/1024/1024/1024}')"
    echo "  $(vm_stat | awk '/Pages active/ {printf "  Active: %.1fGB", $3*4096/1024/1024/1024}')"
    echo "  $(vm_stat | awk '/Pages inactive/ {printf "  Inactive: %.1fGB", $3*4096/1024/1024/1024}')"
    echo "  $(vm_stat | awk '/Memory pressure/ {print "  Pressure: " $3}')"
    echo ""
    
    # CPU Load
    echo "⚡ CPU Status:"
    echo "  Load Average: $(uptime | awk -F'load averages:' '{print $2}')"
    echo "  CPU Usage: $(top -l 1 -n 0 | awk '/CPU usage/ {print $3, $5, $7}')"
    echo ""
    
    # Storage
    echo "💿 Storage Status:"
    df -h | grep -E "(/$|/Volumes)" | while read line; do
        echo "  $line"
    done
    echo ""
    
    # Network Configuration
    echo "🌐 Network Configuration:"
    echo "  TCP Send Buffer: $(sysctl -n net.inet.tcp.sendspace 2>/dev/null || echo "Unknown") bytes"
    echo "  TCP Recv Buffer: $(sysctl -n net.inet.tcp.recvspace 2>/dev/null || echo "Unknown") bytes"
    echo "  RFC1323 Enabled: $(sysctl -n net.inet.tcp.rfc1323 2>/dev/null || echo "Unknown")"
    
    # Network Interface Status
    echo "  Network Interfaces:"
    networksetup -listallhardwareports 2>/dev/null | awk '/Hardware Port/ {print "    " $3 $4 $5; getline; print "      Device: " $2}' || echo "    Unable to list interfaces"
    echo ""
    
    # SMB Mount Status
    echo "📁 SMB Mount Status:"
    smb_mounts=$(mount | grep smb | wc -l)
    echo "  Active SMB mounts: $smb_mounts"
    if [ "$smb_mounts" -gt 0 ]; then
        mount | grep smb | while read mount_line; do
            echo "  $mount_line"
        done
    fi
    echo ""
    
    # Photos App Status
    echo "📸 Photos App Status:"
    photos_pid=$(pgrep Photos 2>/dev/null || echo "")
    if [ -n "$photos_pid" ]; then
        photos_memory=$(ps -o rss= -p "$photos_pid" | awk '{printf "%.1fMB", $1/1024}')
        photos_cpu=$(ps -o %cpu= -p "$photos_pid")
        echo "  Status: Running (PID: $photos_pid)"
        echo "  Memory Usage: $photos_memory"
        echo "  CPU Usage: ${photos_cpu}%"
        
        # Photos settings
        max_memory=$(defaults read com.apple.Photos PMPhotosMaximumMemoryUsage 2>/dev/null || echo "Default")
        cache_size=$(defaults read com.apple.Photos PMPhotosInMemoryCacheSize 2>/dev/null || echo "Default")
        echo "  Max Memory Setting: $max_memory"
        echo "  Cache Size Setting: $cache_size"
    else
        echo "  Status: Not running"
    fi
    echo ""
    
    # Thermal Status
    echo "🌡️  Thermal Status:"
    if command -v powermetrics >/dev/null 2>&1; then
        timeout 5 sudo powermetrics --samplers smc -n 1 2>/dev/null | grep -E "CPU|GPU" | grep "°C" | head -5 || echo "  Thermal data unavailable"
    else
        echo "  Thermal monitoring requires powermetrics"
    fi
    echo ""
    
    # System Optimization Status
    echo "⚙️  Optimization Status:"
    echo "  DSDontWriteNetworkStores: $(defaults read com.apple.desktopservices DSDontWriteNetworkStores 2>/dev/null || echo "Not set")"
    echo "  DSDontWriteUSBStores: $(defaults read com.apple.desktopservices DSDontWriteUSBStores 2>/dev/null || echo "Not set")"
    echo "  Hibernation Mode: $(pmset -g | grep hibernatemode | awk '{print $2}')"
    echo "  Auto Power Off: $(pmset -g | grep autopoweroff | awk '{print $2}')"
    
    # File descriptor limits
    echo "  File Descriptor Limit: $(launchctl limit maxfiles | awk '{print $2}')"
    echo ""
    
    # SlowDisk specific checks
    if [ -d "/Volumes/SlowDisk" ]; then
        echo "🐌 SlowDisk Status:"
        echo "  Mount Point: /Volumes/SlowDisk"
        echo "  Available Space: $(df -h /Volumes/SlowDisk | awk 'NR==2 {print $4}')"
        echo "  Spotlight Indexing: $(mdutil -s /Volumes/SlowDisk 2>/dev/null | grep 'Indexing' | awk '{print $2}' || echo "Unknown")"
        
        # Check mount options
        mount_options=$(mount | grep SlowDisk | sed 's/.*(\(.*\)).*/\1/' || echo "Unknown")
        echo "  Mount Options: $mount_options"
        echo ""
    fi
}

# Network speed test function
network_speed_test() {
    if [ -d "/Volumes/SlowDisk" ]; then
        echo "🚀 Network Speed Test:"
        echo "Testing write speed to SlowDisk..."
        
        # Test write speed
        write_speed=$(time (dd if=/dev/zero of=/Volumes/SlowDisk/speedtest.tmp bs=1m count=100 2>/dev/null) 2>&1 | awk '/real/ {
            split($2, time_parts, "m|s")
            total_seconds = time_parts[1] * 60 + time_parts[2]
            speed_mbps = (100 / total_seconds)
            printf "%.1f MB/s", speed_mbps
        }')
        
        echo "  Write Speed: $write_speed"
        
        # Test read speed
        echo "Testing read speed from SlowDisk..."
        read_speed=$(time (dd if=/Volumes/SlowDisk/speedtest.tmp of=/dev/null bs=1m 2>/dev/null) 2>&1 | awk '/real/ {
            split($2, time_parts, "m|s")
            total_seconds = time_parts[1] * 60 + time_parts[2]
            speed_mbps = (100 / total_seconds)
            printf "%.1f MB/s", speed_mbps
        }')
        
        echo "  Read Speed: $read_speed"
        
        # Cleanup
        rm -f /Volumes/SlowDisk/speedtest.tmp
        echo ""
    else
        warn "SlowDisk not mounted, skipping speed test"
    fi
}

# Main function
main() {
    case "${1:-monitor}" in
        "monitor"|"status")
            monitor_performance
            ;;
        "speed")
            network_speed_test
            ;;
        "continuous")
            echo "Starting continuous monitoring (Ctrl+C to stop)..."
            while true; do
                monitor_performance
                sleep 30
                echo -e "\n${BLUE}Refreshing in 30 seconds...${NC}\n"
            done
            ;;
        "log")
            log_file="/tmp/performance_log_$(date +%Y%m%d_%H%M%S).txt"
            echo "Logging performance data to: $log_file"
            monitor_performance | tee "$log_file"
            echo "Log saved to: $log_file"
            ;;
        *)
            echo "Usage: $0 [monitor|speed|continuous|log]"
            echo ""
            echo "Commands:"
            echo "  monitor     - Show current performance status (default)"
            echo "  speed       - Run network speed test"
            echo "  continuous  - Monitor continuously every 30 seconds"
            echo "  log         - Save performance report to file"
            exit 1
            ;;
    esac
}

# Run main function
main "$@"