class GpsLocation {
  final int vehicleId;
  final double? latitude;
  final double? longitude;
  final double? speed;
  final String status;
  final DateTime? timestamp;

  GpsLocation({
    required this.vehicleId,
    required this.latitude,
    required this.longitude,
    required this.speed,
    required this.status,
    required this.timestamp,
  });

  factory GpsLocation.fromJson(Map<String, dynamic> json) {
    return GpsLocation(
      vehicleId: json["vehicle_id"] as int,
      latitude: (json["latitude"] as num?)?.toDouble(),
      longitude: (json["longitude"] as num?)?.toDouble(),
      speed: (json["speed"] as num?)?.toDouble(),
      status: json["status"] as String,
      timestamp: json["timestamp"] != null ? DateTime.parse(json["timestamp"] as String) : null,
    );
  }

  bool get hasFix => latitude != null && longitude != null;
}

class GpsHistoryPoint {
  final double latitude;
  final double longitude;
  final double? speed;
  final DateTime timestamp;

  GpsHistoryPoint({
    required this.latitude,
    required this.longitude,
    required this.speed,
    required this.timestamp,
  });

  factory GpsHistoryPoint.fromJson(Map<String, dynamic> json) {
    return GpsHistoryPoint(
      latitude: (json["latitude"] as num).toDouble(),
      longitude: (json["longitude"] as num).toDouble(),
      speed: (json["speed"] as num?)?.toDouble(),
      timestamp: DateTime.parse(json["timestamp"] as String),
    );
  }
}
