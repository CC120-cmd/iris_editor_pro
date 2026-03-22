import 'dart:io';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import '../widgets/image_picker_card.dart';
import '../widgets/primary_button.dart';
import 'loading_screen.dart';
import '../utils/usage_limit.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  File? sourceImage;
  File? targetImage;
  bool enhance = false;

  final ImagePicker picker = ImagePicker();

  Future<void> pickImage(bool isSource) async {
    final picked = await picker.pickImage(source: ImageSource.gallery);

    if (picked != null) {
      setState(() {
        if (isSource) {
          sourceImage = File(picked.path);
        } else {
          targetImage = File(picked.path);
        }
      });
    }
  }

  Future<void> processImages() async {
    if (sourceImage == null || targetImage == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text("Please select both images")),
      );
      return;
    }

    bool allowed = await UsageLimit.canUse();

    if (!allowed) {
      showDialog(
        context: context,
        builder: (_) => AlertDialog(
          title: const Text("Limit Reached"),
          content: const Text("You’ve used all free swaps. Upgrade to continue."),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text("OK"),
            )
          ],
        ),
      );
      return;
    }

    await UsageLimit.incrementUsage();

    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (_) => LoadingScreen(
          source: sourceImage!,
          target: targetImage!,
          enhance: enhance,
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Iris Editor Pro"),
        centerTitle: true,
      ),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            ImagePickerCard(
              label: "Pick Source Face",
              image: sourceImage,
              onTap: () => pickImage(true),
            ),
            const SizedBox(height: 16),
            ImagePickerCard(
              label: "Pick Target Image",
              image: targetImage,
              onTap: () => pickImage(false),
            ),
            const SizedBox(height: 16),
            SwitchListTile(
              value: enhance,
              onChanged: (val) => setState(() => enhance = val),
              title: const Text("HD Enhance"),
            ),
            const Spacer(),
            PrimaryButton(
              text: "Swap Faces",
              onPressed: processImages,
            ),
          ],
        ),
      ),
    );
  }
}