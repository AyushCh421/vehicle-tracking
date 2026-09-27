import '../core/api_client.dart';
import '../core/auth_storage.dart';
import '../core/constants.dart';

class AuthService {
  Future<void> login(String username, String password) async {
    final response = await ApiClient.instance.postForm(
      AppConstants.loginEndpoint,
      {"username": username, "password": password},
    );

    final token = response.data["access_token"] as String;
    await AuthStorage.instance.saveToken(token);
  }

  Future<void> logout() async {
    await AuthStorage.instance.clearToken();
  }

  Future<bool> isLoggedIn() async {
    return AuthStorage.instance.hasToken();
  }
}
