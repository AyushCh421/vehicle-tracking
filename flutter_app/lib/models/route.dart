class AppRoute {
  final int id;
  final String name;
  final String routeNumber;
  final String? description;

  AppRoute({
    required this.id,
    required this.name,
    required this.routeNumber,
    this.description,
  });

  factory AppRoute.fromJson(Map<String, dynamic> json) {
    return AppRoute(
      id: json["id"] as int,
      name: json["name"] as String,
      routeNumber: json["route_number"] as String,
      description: json["description"] as String?,
    );
  }
}

class RoutePoint {
  final double latitude;
  final double longitude;
  final int sequence;

  RoutePoint({required this.latitude, required this.longitude, required this.sequence});

  factory RoutePoint.fromJson(Map<String, dynamic> json) {
    return RoutePoint(
      latitude: (json["latitude"] as num).toDouble(),
      longitude: (json["longitude"] as num).toDouble(),
      sequence: json["sequence"] as int,
    );
  }
}
