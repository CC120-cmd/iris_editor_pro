import 'package:shared_preferences/shared_preferences.dart';

class UsageLimit {
  static const int maxFreeUses = 5;
  static const String key = "usage_count";

  static Future<int> getUsage() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getInt(key) ?? 0;
  }

  static Future<void> incrementUsage() async {
    final prefs = await SharedPreferences.getInstance();
    int current = prefs.getInt(key) ?? 0;
    await prefs.setInt(key, current + 1);
  }

  static Future<bool> canUse() async {
    final count = await getUsage();
    return count < maxFreeUses;
  }
}