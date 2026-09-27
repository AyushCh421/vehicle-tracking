import '../core/api_client.dart';
import '../core/constants.dart';
import '../models/route.dart';

class RouteService {
  Future<AppRoute> getMyRoute() async {
    final response = await ApiClient.instance.get(AppConstants.routeEndpoint);
    return AppRoute.fromJson(response.data as Map<String, dynamic>);
  }

  Future<List<RoutePoint>> getMyRoutePoints() async {
    final response = await ApiClient.instance.get(AppConstants.routePointsEndpoint);
    final list = response.data as List;
    return list.map((e) => RoutePoint.fromJson(e as Map<String, dynamic>)).toList();
  }
}
