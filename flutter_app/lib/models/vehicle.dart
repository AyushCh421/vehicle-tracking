class Vehicle {
  final int id;
  final String vehicleNumber;
  final String registrationNumber;
  final String vehicleType;
  final String status;

  Vehicle({
    required this.id,
    required this.vehicleNumber,
    required this.registrationNumber,
    required this.vehicleType,
    required this.status,
  });

  factory Vehicle.fromJson(Map<String, dynamic> json) {
    return Vehicle(
      id: json["id"] as int,
      vehicleNumber: json["vehicle_number"] as String,
      registrationNumber: json["registration_number"] as String,
      vehicleType: json["vehicle_type"] as String,
      status: json["status"] as String,
    );
  }
}
