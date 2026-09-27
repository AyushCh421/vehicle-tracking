import 'package:dio/dio.dart';

import 'auth_storage.dart';
import 'constants.dart';

/// Thrown by ApiClient for any failed request; screens catch this and show
/// [message] directly, per the "meaningful error messages" requirement.
class ApiException implements Exception {
  final String message;
  final int? statusCode;
  ApiException(this.message, {this.statusCode});

  @override
  String toString() => message;
}

/// Centralized Dio-based HTTP client. Attaches the JWT to every request and
/// converts Dio errors into human-readable [ApiException]s.
class ApiClient {
  ApiClient._internal() {
    _dio = Dio(
      BaseOptions(
        baseUrl: AppConstants.baseUrl,
        connectTimeout: const Duration(seconds: 10),
        receiveTimeout: const Duration(seconds: 10),
      ),
    );

    _dio.interceptors.add(
      InterceptorsWrapper(
        onRequest: (options, handler) async {
          final token = await AuthStorage.instance.readToken();
          if (token != null && !options.path.contains(AppConstants.loginEndpoint)) {
            options.headers["Authorization"] = "Bearer $token";
          }
          handler.next(options);
        },
      ),
    );
  }

  static final ApiClient instance = ApiClient._internal();
  late final Dio _dio;

  Future<Response> get(String path, {Map<String, dynamic>? queryParameters}) async {
    try {
      return await _dio.get(path, queryParameters: queryParameters);
    } on DioException catch (e) {
      throw _mapError(e);
    }
  }

  /// Posts form-urlencoded data — required by the backend's OAuth2 password flow.
  Future<Response> postForm(String path, Map<String, dynamic> data) async {
    try {
      return await _dio.post(
        path,
        data: FormData.fromMap(data),
        options: Options(contentType: Headers.multipartFormDataContentType),
      );
    } on DioException catch (e) {
      throw _mapError(e);
    }
  }

  ApiException _mapError(DioException e) {
    if (e.type == DioExceptionType.connectionTimeout ||
        e.type == DioExceptionType.receiveTimeout ||
        e.type == DioExceptionType.connectionError) {
      return ApiException("Unable to connect to server");
    }

    final status = e.response?.statusCode;
    if (status == 401) {
      return ApiException("Session expired", statusCode: 401);
    }
    if (status == 403) {
      return ApiException("You don't have access to this resource", statusCode: 403);
    }
    if (status == 404) {
      return ApiException("Not found", statusCode: 404);
    }

    final detail = e.response?.data is Map ? e.response?.data["detail"] : null;
    if (detail is String) {
      return ApiException(detail, statusCode: status);
    }

    return ApiException("Something went wrong. Please try again.", statusCode: status);
  }
}
