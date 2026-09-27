import 'package:flutter/foundation.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

import 'constants.dart';

/// Thin wrapper around FlutterSecureStorage for the JWT access token.
class AuthStorage {
  AuthStorage._internal();
  static final AuthStorage instance = AuthStorage._internal();

  final _storage = const FlutterSecureStorage();

  // Used only when running the Linux desktop version.
  String? _linuxToken;

  Future<void> saveToken(String token) async {
    if (defaultTargetPlatform == TargetPlatform.linux) {
      _linuxToken = token;
      return;
    }

    await _storage.write(
      key: AppConstants.secureStorageTokenKey,
      value: token,
    );
  }

  Future<String?> readToken() async {
    if (defaultTargetPlatform == TargetPlatform.linux) {
      return _linuxToken;
    }

    return _storage.read(
      key: AppConstants.secureStorageTokenKey,
    );
  }

  Future<void> clearToken() async {
    if (defaultTargetPlatform == TargetPlatform.linux) {
      _linuxToken = null;
      return;
    }

    await _storage.delete(
      key: AppConstants.secureStorageTokenKey,
    );
  }

  Future<bool> hasToken() async {
    final token = await readToken();
    return token != null && token.isNotEmpty;
  }
}