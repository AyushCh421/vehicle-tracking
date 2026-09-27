import 'dart:async';

import 'package:flutter/material.dart';
import 'package:intl/intl.dart';

import '../core/api_client.dart';
import '../core/constants.dart';
import '../models/route.dart';
import '../models/vehicle.dart';
import '../models/gps_location.dart';
import '../models/user.dart';
import '../services/auth_service.dart';
import '../services/route_service.dart';
import '../services/vehicle_service.dart';
import 'login_screen.dart';
import 'map_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final _routeService = RouteService();
  final _vehicleService = VehicleService();
  final _authService = AuthService();

  bool _isLoading = true;
  String? _errorMessage;

  AppUser? _user;
  AppRoute? _route;
  Vehicle? _vehicle;
  GpsLocation? _location;

  Timer? _pollTimer;

  @override
  void initState() {
    super.initState();
    _loadInitialData();
  }

  @override
  void dispose() {
    _pollTimer?.cancel();
    super.dispose();
  }

  Future<void> _loadInitialData() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final userResp = await ApiClient.instance.get(AppConstants.meEndpoint);
      final user = AppUser.fromJson(userResp.data as Map<String, dynamic>);

      final results = await Future.wait([
        _routeService.getMyRoute(),
        _vehicleService.getMyVehicle(),
        _vehicleService.getMyVehicleLocation(),
      ]);

      setState(() {
        _user = user;
        _route = results[0] as AppRoute;
        _vehicle = results[1] as Vehicle;
        _location = results[2] as GpsLocation?;
        _isLoading = false;
      });

      _startPolling();
    } on ApiException catch (e) {
      setState(() {
        _errorMessage = e.message;
        _isLoading = false;
      });
      if (e.statusCode == 401) _handleSessionExpired();
    } catch (_) {
      setState(() {
        _errorMessage = "Unable to connect to server";
        _isLoading = false;
      });
    }
  }

  void _startPolling() {
    _pollTimer?.cancel();
    _pollTimer = Timer.periodic(AppConstants.locationPollInterval, (_) => _refreshLocation());
  }

  Future<void> _refreshLocation() async {
    try {
      final location = await _vehicleService.getMyVehicleLocation();
      final vehicle = await _vehicleService.getMyVehicle(); // keeps status (ACTIVE/OFFLINE) fresh
      if (!mounted) return;
      setState(() {
        _location = location;
        _vehicle = vehicle;
      });
    } on ApiException catch (e) {
      if (e.statusCode == 401) _handleSessionExpired();
      // Otherwise fail silently on a background poll tick — don't spam the user.
    } catch (_) {
      // Network hiccup on a poll tick; next tick will retry.
    }
  }

  void _handleSessionExpired() {
    _pollTimer?.cancel();
    if (!mounted) return;
    Navigator.of(context).pushAndRemoveUntil(
      MaterialPageRoute(builder: (_) => const LoginScreen()),
      (route) => false,
    );
  }

  Future<void> _handleLogout() async {
    _pollTimer?.cancel();
    await _authService.logout();
    if (!mounted) return;
    Navigator.of(context).pushAndRemoveUntil(
      MaterialPageRoute(builder: (_) => const LoginScreen()),
      (route) => false,
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Vehicle Tracker"),
        actions: [
          IconButton(icon: const Icon(Icons.logout), onPressed: _handleLogout, tooltip: "Log out"),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: _loadInitialData,
        child: _buildBody(),
      ),
    );
  }

  Widget _buildBody() {
    if (_isLoading) {
      return const Center(child: CircularProgressIndicator());
    }

    if (_errorMessage != null && _user == null) {
      return ListView(
        children: [
          const SizedBox(height: 120),
          Icon(Icons.wifi_off, size: 48, color: Colors.grey.shade400),
          const SizedBox(height: 12),
          Center(child: Text(_errorMessage!, style: const TextStyle(color: Colors.red))),
          const SizedBox(height: 12),
          Center(
            child: OutlinedButton(onPressed: _loadInitialData, child: const Text("Retry")),
          ),
        ],
      );
    }

    final isActive = _vehicle?.status == "ACTIVE";
    final timeFormat = DateFormat("HH:mm:ss");

    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        Text("Welcome, ${_user?.fullName ?? ''}", style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
        const SizedBox(height: 20),
        _SectionCard(
          title: "Route",
          children: [
            _InfoRow(label: _route?.name ?? '-', value: _route?.routeNumber ?? ''),
            if (_route?.description != null && _route!.description!.isNotEmpty)
              Padding(
                padding: const EdgeInsets.only(top: 4),
                child: Text(_route!.description!, style: TextStyle(color: Colors.grey.shade600)),
              ),
          ],
        ),
        const SizedBox(height: 16),
        _SectionCard(
          title: "Vehicle",
          children: [
            _InfoRow(label: _vehicle?.vehicleNumber ?? '-', value: _vehicle?.registrationNumber ?? ''),
            const SizedBox(height: 8),
            Row(
              children: [
                Icon(Icons.circle, size: 10, color: isActive ? Colors.green : Colors.grey),
                const SizedBox(width: 6),
                Text(
                  "Status: ${_vehicle?.status ?? 'UNKNOWN'}",
                  style: TextStyle(
                    fontWeight: FontWeight.w600,
                    color: isActive ? Colors.green.shade700 : Colors.grey.shade600,
                  ),
                ),
              ],
            ),
          ],
        ),
        const SizedBox(height: 16),
        _SectionCard(
          title: "Current GPS",
          children: _location != null && _location!.hasFix
              ? [
                  _InfoRow(label: "Latitude", value: _location!.latitude!.toStringAsFixed(5)),
                  _InfoRow(label: "Longitude", value: _location!.longitude!.toStringAsFixed(5)),
                  _InfoRow(
                    label: "Speed",
                    value: _location!.speed != null ? "${_location!.speed!.toStringAsFixed(1)} km/h" : "-",
                  ),
                  _InfoRow(
                    label: "Last Updated",
                    value: _location!.timestamp != null ? timeFormat.format(_location!.timestamp!.toLocal()) : "-",
                  ),
                ]
              : [
                  Row(
                    children: [
                      Icon(Icons.location_off, color: Colors.grey.shade400),
                      const SizedBox(width: 8),
                      const Text("No GPS data available"),
                    ],
                  ),
                ],
        ),
        const SizedBox(height: 24),
        ElevatedButton.icon(
          icon: const Icon(Icons.map),
          label: const Text("View Map"),
          style: ElevatedButton.styleFrom(padding: const EdgeInsets.symmetric(vertical: 14)),
          onPressed: () {
            Navigator.of(context).push(MaterialPageRoute(builder: (_) => const MapScreen()));
          },
        ),
      ],
    );
  }
}

class _SectionCard extends StatelessWidget {
  final String title;
  final List<Widget> children;

  const _SectionCard({required this.title, required this.children});

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 1,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(title, style: TextStyle(fontSize: 14, fontWeight: FontWeight.w600, color: Colors.grey.shade600)),
            const SizedBox(height: 10),
            ...children,
          ],
        ),
      ),
    );
  }
}

class _InfoRow extends StatelessWidget {
  final String label;
  final String value;

  const _InfoRow({required this.label, required this.value});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 2),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w500)),
          Text(value, style: TextStyle(fontSize: 14, color: Colors.grey.shade700)),
        ],
      ),
    );
  }
}
