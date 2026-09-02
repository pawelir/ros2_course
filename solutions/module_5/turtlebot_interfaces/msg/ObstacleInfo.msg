# Closest obstacle seen by the laser scanner.
std_msgs/Header header
float32 distance        # [m] smallest valid range
float32 angle           # [rad] bearing of that range in the scan frame (0 = straight ahead)
bool blocked            # true if distance < stop_distance
