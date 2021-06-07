import 'package:flutter/services.dart' show DeviceOrientation, SystemChrome;
import 'package:android_flickr/screens/get_started_page_screen.dart';
import 'package:android_flickr/screens/click_on_image_screen.dart';
import 'package:android_flickr/screens/flickr_camera_screen.dart';
import 'package:android_flickr/screens/non_profile_screen.dart';
import 'package:android_flickr/providers/flickr_profiles.dart';
import 'package:android_flickr/providers/flickr_posts.dart';
import 'package:android_flickr/screens/explore_screen.dart';
import 'package:android_flickr/screens/search_screen.dart';
import 'package:android_flickr/screens/splash_screen.dart';
import 'package:onesignal_flutter/onesignal_flutter.dart';
import 'package:android_flickr/providers/auth.dart';
import 'package:splashscreen/splashscreen.dart';
import 'colors/black_swatch.dart' as primBlack;
import 'package:provider/provider.dart';
import 'package:flutter/material.dart';
import './providers/auth.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'Classes/globals.dart' as globals;
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:flutter/services.dart';
import 'dart:io';
import './providers/flickr_groups.dart';
// import 'package:android_flickr/providers/flickr_post.dart';
// import 'package:android_flickr/screens/group_view.dart';
// import 'package:android_flickr/screens/new_discussion.dart';
// import 'package:android_flickr/widgets/explore_display.dart';
// import 'package:android_flickr/screens/flickr_Camera_Screen.dart';
// import './screens/login_screen.dart';
// import 'screens/photo_edit_screen.dart';
// import 'package:shared_preferences/shared_preferences.dart';
// import 'Classes/globals.dart' as globals;
// import './providers/auth.dart' as auth;
// import 'package:http/http.dart' as http;
// import 'dart:convert';
// import 'dart:io';
//import './providers/flickr_post.dart';

/// Main function, before App runs, we check user preferences for remember email flag,
///  if true, we call the sign up request method to get access and refresh token and start app in explore screen,
///  if false we start app in get started screen.
void main() async {
  //if real server, Get remember me flag from user pref, if true, login and go to explore
  if (!globals.isMockService) {
    WidgetsFlutterBinding.ensureInitialized();
    SharedPreferences prefs = await SharedPreferences.getInstance();
    globals.rememberMe = prefs.getBool('remember') ?? false;
    globals.rememberMe = false;
    print(globals.rememberMe);
    if (globals.rememberMe) {
      var url = Uri.https(globals.HttpSingleton().getBaseUrl(),
          globals.isMockService ? '/login/' : 'api/accounts/login/');
      final response = await http.post(url,
          body: json.encode(
            {
              'email': prefs.getString('email'),
              'password': prefs.getString('password'),
            },
          ),
          headers: {HttpHeaders.contentTypeHeader: 'application/json'});
      if (response.statusCode == 200) {
        final Map<String, dynamic> data = json.decode(response.body);
        globals.accessToken = data['tokens']['access'];
        globals.refreshToken = data['tokens']['refresh'];
        globals.email = prefs.getString('email');
        globals.password = prefs.getString('password');
      }
      print(json.decode(response.body));
    }
    WidgetsFlutterBinding.ensureInitialized();
  }
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  // This widget is the root of the application.
  @override
  Widget build(BuildContext context) {
    //make app work only in portrait
    SystemChrome.setPreferredOrientations(
      [
        DeviceOrientation.portraitUp,
        DeviceOrientation.portraitDown,
      ],
    );

    ///Remove this method to stop OneSignal Debugging
    OneSignal.shared.setLogLevel(OSLogLevel.verbose, OSLogLevel.none);

    OneSignal.shared.init("494522f0-cedd-4d54-b99b-c12ac52f66a6", iOSSettings: {
      OSiOSSettings.autoPrompt: false,
      OSiOSSettings.inAppLaunchUrl: false
    });
    OneSignal.shared
        .setInFocusDisplayType(OSNotificationDisplayType.notification);

    /// will be called whenever a notification is received
    OneSignal.shared
        .setNotificationReceivedHandler((OSNotification notification) {});

    /// will be called whenever a notification is opened/button pressed.
    OneSignal.shared
        .setNotificationOpenedHandler((OSNotificationOpenedResult result) {
      globals.notifications.add(result);
      print(result);
    });

    var status =
        OneSignal.shared.getPermissionSubscriptionState().then((value) {
      print('Zaka ' + value.subscriptionStatus.userId);
    });

    return MultiProvider(
      providers: [
        ChangeNotifierProvider.value(
          value: YourGroups(),
        ),
        ChangeNotifierProvider.value(
          value: Auth(),
        ),
        ChangeNotifierProvider(
          create: (ctx) => Posts(),
        ),
        ChangeNotifierProvider(
          create: (ctx) => FlickrProfiles(),
        ),
        ChangeNotifierProvider(
          create: (ctx) => MyProfile(),
        ),
      ],
      child: MaterialApp(
        // onGenerateRoute: (settings) {
        //   if (settings.name == SearchScreen.routeName) {
        //     return MaterialPageRoute(
        //       builder: (ctx) => SearchScreen(),
        //     );
        //   }
        // },
        title: 'Flickr',
        debugShowCheckedModeBanner: false,
        theme: ThemeData(
          fontFamily: 'Proxima Nova',
          primarySwatch: primBlack.primaryBlack,
          visualDensity: VisualDensity.adaptivePlatformDensity,
        ),
        home: FlickrSplashScreen(
          globals.accessToken == '' ? GetStartedScreen() : ExploreScreen(),
          globals.accessToken == '' ? true : false,
        ),
        //NonProfileScreen()
        //FlickrSplashScreen(GetStartedScreen(), true),
        routes: {
          ExploreScreen.routeName: (ctx) => ExploreScreen(),
          ClickOnImageScreen.routeName: (ctx) => ClickOnImageScreen(),
          GetStartedScreen.routeName: (ctx) => GetStartedScreen(),
          //FlickrSplashScreen.routeName: (ctx) => FlickrSplashScreen(),
          SearchScreen.routeName: (ctx) => SearchScreen(),
          NonProfileScreen.routeName: (ctx) => NonProfileScreen(),
          FlickrCameraScreen.routeName: (ctx) => FlickrCameraScreen(),
        },
      ),
    );
  }
}
