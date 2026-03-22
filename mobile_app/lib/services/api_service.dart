import 'dart:io';
import 'package:http/http.dart' as http;
import '../core/constants.dart';

class ApiService {
  static Future<File> processImage(
    File source,
    File target,
    bool enhance,
  ) async {
    try {
      var uri = Uri.parse("${Constants.baseUrl}/swap");

      var request = http.MultipartRequest("POST", uri);

      request.files.add(
        await http.MultipartFile.fromPath("source", source.path),
      );

      request.files.add(
        await http.MultipartFile.fromPath("target", target.path),
      );

      request.fields["enhance"] = enhance.toString();

      var response = await request.send();

      if (response.statusCode != 200) {
        final errorBody = await response.stream.bytesToString();
        throw Exception("Server error: $errorBody");
      }

      var bytes = await response.stream.toBytes();

      final filePath = "${source.parent.path}/result_${DateTime.now().millisecondsSinceEpoch}.jpg";
      final file = File(filePath);

      await file.writeAsBytes(bytes);

      return file;
    } catch (e) {
      throw Exception("Processing failed: $e");
    }
  }
}