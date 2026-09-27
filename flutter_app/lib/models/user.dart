class AppUser {
  final int id;
  final String username;
  final String fullName;
  final int routeId;
  final int vehicleId;

  AppUser({
    required this.id,
    required this.username,
    required this.fullName,
    required this.routeId,
    required this.vehicleId,
  });

  factory AppUser.fromJson(Map<String, dynamic> json) {
    return AppUser(
      id: json["id"] as int,
      username: json["username"] as String,
      fullName: json["full_name"] as String,
      routeId: json["route_id"] as int,
      vehicleId: json["vehicle_id"] as int,
    );
  }
}
