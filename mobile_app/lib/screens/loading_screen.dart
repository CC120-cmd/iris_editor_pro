import 'dart:io';
import 'package:flutter/material.dart';
import '../services/api_service.dart';
import 'preview_screen.dart';

class LoadingScreen extends StatefulWidget {
  final File source;
  final File target;
  final bool enhance;

  const LoadingScreen({
    super.key,
    required this.source,
    required this.target,
    required this.enhance,
  });

  @override
  State<LoadingScreen> createState() => _LoadingScreenState();
}

class _LoadingScreenState extends State<LoadingScreen> {

  @override
  void initState() {
    super.initState();
    processImage();
  }

  Future<void> processImage() async {
    try {
      final result = await ApiService.processImage(
        widget.source,
        widget.target,
        widget.enhance,
      );

      if (!mounted) return;

      Navigator.pushReplacement(
        context,
        MaterialPageRoute(
          builder: (_) => PreviewScreen(image: result),
        ),
      );
    } catch (e) {
      if (!mounted) return;

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(e.toString())),
      );

      Navigator.pop(context);
    }
  }

  @override
  Widget build(BuildContext context) {
    return const Scaffold(
      body: Center(
        child: CircularProgressIndicator(),
      ),
    );
  }
}