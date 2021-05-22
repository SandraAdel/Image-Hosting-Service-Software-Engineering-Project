import 'package:flutter_test/flutter_test.dart';
import '../lib/Classes/globals.dart' as globals;

void main() {
  group('HttpSingleton', () {
    test('Baseurl_Mock_true', () {
      //Arrange
      bool original = globals.isMockService;
      globals.isMockService = true;
      String matcher = '10.0.2.2:3000';
      //Act
      String actual = globals.HttpSingleton().getBaseUrl();
      //Assert
      expect(actual, matcher);
      globals.isMockService = original;
    });
    test('Baseurl_Mock_false', () {
      //Arrange
      bool original = globals.isMockService;
      globals.isMockService = false;
      String matcher = 'https://fotone.me/api';
      //Act
      String actual = globals.HttpSingleton().getBaseUrl();
      //Assert
      expect(actual, matcher);
      globals.isMockService = original;
    });
  });
}
