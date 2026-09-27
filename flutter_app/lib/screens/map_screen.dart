import 'dart:async';

import 'package:flutter/material.dart';
import 'package:google_maps_flutter/google_maps_flutter.dart';

import '../core/api_client.dart';
import '../core/constants.dart';
import '../models/route.dart';
import '../models/gps_location.dart';
import '../services/route_service.dart';
import '../services/vehicle_service.dart';

/// Draws the assigned route as a polyline and the vehicle's current
/// position as a marker. All coordinates come from the backend — nothing
/// here is hardcoded.
class MapScreen extends StatefulWidget {
  const MapScreen({super.key});

  @override
  State<MapScreen> createState() => _MapScreenState();
}

class _MapScreenState extends State<MapScreen> {
  final _routeService = RouteService();
  final _vehicleService = VehicleService();

  GoogleMapController? _mapController;
  Timer? _pollTimer;

  bool _isLoading = true;
  String? _errorMessage;

  Set<Polyline> _polylines = {};
  Set<Marker> _markers = {};
  LatLng? _initialCameraTarget;

  @override
  void initState() {
    super.initState();
    _loadRouteAndStartTracking();
  }

  @override
  void dispose() {
    _pollTimer?.cancel();
    super.dispose();
  }

  Future<void> _loadRouteAndStartTracking() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final points = await _routeService.getMyRoutePoints();
      if (points.isNotEmpty) {
        _polylines = {
          Polyline(
            polylineId: const PolylineId("assigned_route"),
            color: Colors.indigo,
            width: 4,
            points: points.map((p) => LatLng(p.latitude, p.longitude)).toList(),
          ),
        };
        _initialCameraTarget = LatLng(points.first.latitude, points.first.longitude);
      }

      await _refreshVehicleLocation();

      setState(() => _isLoading = false);
      _pollTimer = Timer.periodic(AppConstants.locationPollInterval, (_) => _refreshVehicleLocation());
    } on ApiException catch (e) {
      setState(() {
        _errorMessage = e.message;
        _isLoading = false;
      });
    } catch (_) {
      setState(() {
        _errorMessage = "Unable to connect to server";
        _isLoading = false;
      });
    }
  }

  Future<void> _refreshVehicleLocation() async {
    try {
      final GpsLocation? location = await _vehicleService.getMyVehicleLocation();
      if (!mounted) return;

      if (location != null && location.hasFix) {
        final position = LatLng(location.latitude!, location.longitude!);
        setState(() {
          _markers = {
            Marker(
              markerId: const MarkerId("vehicle"),
              position: position,
              icon: BitmapDescriptor.defaultMarkerWithHue(BitmapDescriptor.hueAzure),
              infoWindow: InfoWindow(
                title: "Vehicle",
                snippet: location.speed != null ? "${location.speed!.toStringAsFixed(1)} km/h" : null,
              ),
            ),
          };
        });
        _initialCameraTarget ??= position;
        _mapController?.animateCamera(CameraUpdate.newLatLng(position));
      }
    } catch (_) {
      // Silent on background poll ticks; the map keeps its last known state.
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Route Map")),
      body: _buildBody(),
    );
  }

  Widget _buildBody() {
    if (_isLoading) {
      return const Center(child: CircularProgressIndicator());
    }

    if (_errorMessage != null && _polylines.isEmpty) {
      return Center(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(Icons.map_outlined, size: 48, color: Colors.grey.shade400),
              const SizedBox(height: 12),
              Text(_errorMessage!, textAlign: TextAlign.center, style: const TextStyle(color: Colors.red)),
              const SizedBox(height: 12),
              OutlinedButton(onPressed: _loadRouteAndStartTracking, child: const Text("Retry")),
            ],
          ),
        ),
      );
    }

    if (_initialCameraTarget == null) {
      return const Center(child: Text("No GPS data available"));
    }

    return GoogleMap(
      initialCameraPosition: CameraPosition(target: _initialCameraTarget!, zoom: 14),
      onMapCreated: (controller) => _mapController = controller,
      polylines: _polylines,
      markers: _markers,
      myLocationButtonEnabled: false,
    );
  }
}
