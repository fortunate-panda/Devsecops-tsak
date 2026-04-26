def check_for_anomaly(current_ip_rate, current_ip_errors, baseline):
    mean, std_dev, error_mean = baseline.get_stats()
    
    # 1. Check Z-Score for traffic volume
    z_score = (current_ip_rate - mean) / std_dev
    
    # 2. Check for Error Surge (3x more than baseline)
    is_error_surge = current_ip_errors > (error_mean * 3) and current_ip_errors > 5

    if z_score > 3.0:
        return True, f"High Volume Anomaly (Z-Score: {z_score:.2f})"
    
    if is_error_surge:
        return True, f"Error Surge Detected ({current_ip_errors} errors)"
        
    return False, None