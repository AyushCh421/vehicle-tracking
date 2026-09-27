/// App-wide constants. Change [baseUrl] to point at your backend.
///
/// - Android emulator talking to a host machine's localhost: 10.0.2.2
/// - Linux desktop: localhost
/// - iOS simulator: localhost
/// - Physical device: your machine's LAN IP
class AppConstants {
  AppConstants._();

  static const String baseUrl = "http://localhost:8000";

  static const String loginEndpoint = "/api/auth/login";
  static const String meEndpoint = "/api/users/me";
  static const String routeEndpoint = "/api/routes/me";
  static const String routePointsEndpoint = "/api/routes/me/points";
  static const String vehicleEndpoint = "/api/vehicles/me";
  static const String vehicleLocationEndpoint = "/api/vehicles/me/location";
  static const String vehicleHistoryEndpoint = "/api/vehicles/me/history";

  static const Duration locationPollInterval = Duration(seconds: 5);

  static const String secureStorageTokenKey = "access_token";
}