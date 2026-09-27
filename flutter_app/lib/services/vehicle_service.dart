import '../core/api_client.dart';
import '../core/constants.dart';
import '../models/gps_location.dart';
import '../models/vehicle.dart';

class VehicleService {
  Future<Vehicle> getMyVehicle() async {
    final response = await ApiClient.instance.get(AppConstants.vehicleEndpoint);
    return Vehicle.fromJson(response.data as Map<String, dynamic>);
  }

  /// Returns null when the backend has no location yet (404) rather than
  /// throwing, so the UI can show a friendly "No GPS data available" state.
  Future<GpsLocation?> getMyVehicleLocation() async {
    try {
      final response = await ApiClient.instance.get(AppConstants.vehicleLocationEndpoint);
      return GpsLocation.fromJson(response.data as Map<String, dynamic>);
    } on ApiException catch (e) {
      if (e.statusCode == 404) return null;
      rethrow;
    }
  }

  Future<List<GpsHistoryPoint>> getMyVehicleHistory({int limit = 100}) async {
    final response = await ApiClient.instance.get(
      AppConstants.vehicleHistoryEndpoint,
      queryParameters: {"limit": limit},
    );
    final list = response.data as List;
    return list.map((e) => GpsHistoryPoint.fromJson(e as Map<String, dynamic>)).toList();
  }
}
