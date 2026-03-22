import 'dart:io';
import 'package:flutter/material.dart';

class ImagePickerCard extends StatelessWidget {
  final String label;
  final File? image;
  final VoidCallback onTap;

  const ImagePickerCard({
    super.key,
    required this.label,
    required this.image,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        height: 160,
        width: double.infinity,
        decoration: BoxDecoration(
          color: Colors.grey[900],
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: Colors.white12),
        ),
        child: image == null
            ? Center(
                child: Text(
                  label,
                  style: const TextStyle(color: Colors.white70),
                ),
              )
            : ClipRRect(
                borderRadius: BorderRadius.circular(16),
                child: Image.file(
                  image!,
                  fit: BoxFit.cover,
                ),
              ),
      ),
    );
  }
}