import 'package:android_flickr/providers/flickr_posts.dart';
import 'package:android_flickr/screens/click_on_image_screen.dart';
import 'package:android_flickr/screens/explore_screen.dart';
import 'package:android_flickr/screens/flickr_Camera_Screen.dart';
import 'package:android_flickr/screens/get_started_page_screen.dart';
import 'package:android_flickr/screens/group_view.dart';
import 'package:android_flickr/screens/new_discussion.dart';
import 'package:android_flickr/screens/non_profile_screen.dart';
import 'package:android_flickr/screens/splash_screen.dart';
import 'package:android_flickr/widgets/Explore_display.dart';
//import 'package:android_flickr/screens/flickr_Camera_Screen.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart' show DeviceOrientation, SystemChrome;
import 'package:provider/provider.dart';
import './colors/blackSwatch.dart' as primBlack;
import './screens/login_screen.dart';
import './screens/photoEditScreen.dart';
import 'package:onesignal_flutter/onesignal_flutter.dart';

//import './providers/flickr_post.dart';

void main() {
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
//Remove this method to stop OneSignal Debugging
    OneSignal.shared.setLogLevel(OSLogLevel.verbose, OSLogLevel.none);

    OneSignal.shared.init("494522f0-cedd-4d54-b99b-c12ac52f66a6", iOSSettings: {
      OSiOSSettings.autoPrompt: false,
      OSiOSSettings.inAppLaunchUrl: false
    });
    OneSignal.shared
        .setInFocusDisplayType(OSNotificationDisplayType.notification);
    OneSignal.shared
        .setNotificationReceivedHandler((OSNotification notification) {
      // will be called whenever a notification is received
    });

    OneSignal.shared
        .setNotificationOpenedHandler((OSNotificationOpenedResult result) {
      // will be called whenever a notification is opened/button pressed.
    });
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(
          create: (ctx) => Posts(),
        )
      ],
      child: MaterialApp(
        title: 'Flickr',
        debugShowCheckedModeBanner: false,
        theme: ThemeData(
          fontFamily: 'Rubik',
          primarySwatch: primBlack.primaryBlack,
          visualDensity: VisualDensity.adaptivePlatformDensity,
        ),
        home: FlickrSplashScreen(
          ExploreScreen(),
        ),
        //NonProfileScreen()
        /*  FlickrSplashScreen(
          GetStartedScreen(),
        ), */
        routes: {
          ExploreScreen.routeName: (ctx) => ExploreScreen(),
          ClickOnImageScreen.routeName: (ctx) => ClickOnImageScreen(),
          GetStartedScreen.routeName: (ctx) => GetStartedScreen(),
          //FlickrSplashScreen.routeName: (ctx) => FlickrSplashScreen(),
        },
      ),
    );
  }
}
