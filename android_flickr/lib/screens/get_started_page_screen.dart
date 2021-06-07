//import 'dart:js';
//import 'dart:ui';
//import 'package:http/http.dart' as http;
// import 'package:android_flickr/screens/explore_screen.dart';
import 'package:android_flickr/screens/explore_screen.dart';
import 'package:android_flickr/screens/logIn_screen.dart';
import 'package:flutter/material.dart';
import 'package:flutter_swiper/flutter_swiper.dart';
import './splash_screen.dart';
import '../Classes/globals.dart' as globals;

enum SlideNumber {
  slide1,
  slide2,
  slide3,
  slide4,
}

///The first screen that appears when the user is not logged in.
class GetStartedScreen extends StatefulWidget {
  static const routeName = '/get-started-screen';
  @override
  GetStartedScreenState createState() => GetStartedScreenState();
}

class GetStartedScreenState extends State<GetStartedScreen> {
  ///The images are preloaded from the assests in this map and so they are ready to be displayed .
  Map<String, Image> swipeImageMap;

  ///contains first swipe image.
  Image swipeImage1;

  ///contains second swipe image.
  Image swipeImage2;

  ///contains third swipe image.
  Image swipeImage3;

  ///contains forth swipe image.
  Image swipeImage4;

  /// Returns the String to be displayed as title based on the Swipe image we are on.
  String setStartedScreenTitle(int index) {
    switch (index) {
      case 0:
        return 'Powerful';
        break;
      case 1:
        return 'Keep your memories safe';
        break;
      case 2:
        return 'Organisation simpified';
        break;
      case 3:
        return 'Sharing made easy';
        break;
      default:
        return 'Unknown';
    }
  }

  /// Returns the String to be dsplayed as subtitle based on the Swipe image we are on.
  String setStartedScreenSubTitle(int index) {
    switch (index) {
      case 0:
        return 'Save all of your photos and videos in one place.';
        break;
      case 1:
        return 'Your uploaded photos stay private until you choose to share them.';
        break;
      case 2:
        return 'Search, edit and organise in seconds.';
        break;
      case 3:
        return 'Share with friends, family and the world.';
        break;
      default:
        return 'Unknown';
    }
  }

  ///push explore screen
  void exploreScreen(BuildContext ctx) {
    Navigator.of(ctx).push(
      MaterialPageRoute(
        builder: (context) => FlickrSplashScreen(
          globals.isMockService ? ExploreScreen() : LogIn(),
          globals.isMockService ? false : true,
        ),
      ),
    );
  }

  @override
  void initState() {
    /// To preload the 4 images on started screen from assets and avoid white background.
    swipeImage1 = Image.asset(
      'assets/images/GetStartedScreens/GetStartedScreenSlide1.png',
      alignment: Alignment.center,
      fit: BoxFit.cover,
      height: double.infinity,
      width: double.infinity,
    );
    swipeImage2 = Image.asset(
      'assets/images/GetStartedScreens/GetStartedScreenSlide2.png',
      alignment: Alignment.center,
      fit: BoxFit.cover,
      height: double.infinity,
      width: double.infinity,
    );
    swipeImage3 = Image.asset(
      'assets/images/GetStartedScreens/GetStartedScreenSlide3.png',
      alignment: Alignment.center,
      fit: BoxFit.cover,
      height: double.infinity,
      width: double.infinity,
    );
    swipeImage4 = Image.asset(
      'assets/images/GetStartedScreens/GetStartedScreenSlide4.png',
      alignment: Alignment.center,
      fit: BoxFit.cover,
      height: double.infinity,
      width: double.infinity,
    );

    swipeImageMap = {
      'swipeImage1': swipeImage1,
      'swipeImage2': swipeImage2,
      'swipeImage3': swipeImage3,
      'swipeImage4': swipeImage4,
    };
    // print(swipeImageMap.keys.first);

    super.initState();
  }

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();

    /// Preloades the images from app to the cache so they can be displayed immediately.
    precacheImage(swipeImage1.image, context);
    precacheImage(swipeImage2.image, context);
    precacheImage(swipeImage3.image, context);
    precacheImage(swipeImage4.image, context);
  }

  @override
  Widget build(BuildContext context) {
    /// Returns scaffold where we set the Title, subtitle, button, SwipeImages and author name on stack.

    return Scaffold(
      body: Container(
        padding: EdgeInsets.only(
          top: MediaQuery.of(context).padding.top,
        ),
        height: MediaQuery.of(context).size.height,
        child: Stack(
          children: [
            Container(
              height: double.infinity,
              width: double.infinity,
              child: Swiper(
                /// We also use Swiper widget so we can swipe between images and titles and subtitles.
                containerWidth: double.infinity,
                itemCount: 4,
                loop: false,
                controller: SwiperController(),
                itemBuilder: (ctx, index) {
                  return Stack(
                    children: [
                      swipeImageMap['swipeImage' + '${index + 1}'],
                      Positioned(
                        top: MediaQuery.of(context).size.height / 1.75,
                        left: MediaQuery.of(context).size.width / 11,
                        child: Container(
                          width: MediaQuery.of(context).size.width -
                              MediaQuery.of(context).size.width / 5.5,
                          alignment: Alignment.center,
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.center,
                            children: [
                              Text(
                                setStartedScreenTitle(index),
                                style: TextStyle(
                                  color: Colors.white,
                                  fontSize: 20,
                                  fontWeight: FontWeight.bold,
                                ),
                                softWrap: true,
                                textAlign: TextAlign.center,
                              ),
                              SizedBox(
                                height: 10,
                              ),
                              Text(
                                setStartedScreenSubTitle(index),
                                style: TextStyle(
                                  color: Colors.white,
                                  fontSize: 15,
                                ),
                                softWrap: true,
                                textAlign: TextAlign.center,
                              ),
                            ],
                          ),
                        ),
                      ),
                    ],
                  );
                },
                //viewportFraction: 1.5,
                scale: 1,
                pagination: SwiperPagination(),
              ),
            ),
            Positioned(
              /// Postion the app name on stack.
              top: MediaQuery.of(context).size.height / 5,
              //left: MediaQuery.of(context).size.width / 3.5,
              child: Container(
                width: MediaQuery.of(context).size.width,
                child: Text(
                  "flickr",
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 70,
                    fontWeight: FontWeight.bold,
                  ),
                  textAlign: TextAlign.center,
                ),
              ),
            ),
            Positioned(
              /// Postion the flat button on stack.
              height: MediaQuery.of(context).size.height * 1.65,
              left: MediaQuery.of(context).size.width / 8,
              child: Container(
                alignment: Alignment.center,
                width: MediaQuery.of(context).size.width -
                    MediaQuery.of(context).size.width / 3.7,
                child: InkWell(
                  splashColor: Colors.blue,
                  child: FlatButton(
                    shape: Border.all(
                      color: Colors.white,
                      width: 1,
                    ),
                    height: 60,
                    minWidth: double.infinity,
                    onPressed: () => exploreScreen(context),
                    child: Text(
                      "Get started",
                      style: TextStyle(
                        color: Colors.white,
                      ),
                      textAlign: TextAlign.center,
                    ),
                    color: Colors.transparent,
                  ),
                ),
              ),
            ),

            /// Postion the author name on stack.
            Positioned(
              height: MediaQuery.of(context).size.height * 1.88,
              left: 10,
              child: Row(
                children: [
                  Icon(
                    Icons.camera_alt,
                    color: Colors.white,
                  ),
                  SizedBox(
                    width: 5,
                  ),
                  Text(
                    "Ben Flasher",
                    style: TextStyle(
                      color: Colors.white,
                    ),
                  ),
                ],
              ),
            )
          ],
        ),
      ),
    );
  }
}
