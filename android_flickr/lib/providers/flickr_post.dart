import 'package:flutter/cupertino.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:flutter/foundation.dart';
import '../Classes/globals.dart' as globals;
import '../providers/flickr_posts.dart';

///Class PicPosterDetails describes few information about the user who posted the picture and these info are his name and whether
///he is a pro or not and if he is followed by the current user(the person using the application) as well as his profile picture url.
class PicPosterDetails with ChangeNotifier {
  String profileId;
  String name;
  bool isPro;
  bool isFollowedByUser;
  bool followedDuringRunning = false;
  String profilePicUrl;
  String profileCoverPhoto;
  PicPosterDetails(
    this.profileId,
    this.name,
    this.isPro,
    this.isFollowedByUser,
    this.profilePicUrl,
    this.profileCoverPhoto,
  );
  void notify() {
    notifyListeners();
  }
}

///Class FavedPostDetails this class describes the post fave details which is how many users faved the post as well as
///one or two names (if there is anyone who faved) two display below the image and whether the user faved the post or no.
class FavedPostDetails {
  int favesTotalNumber;
  List<String> favedUsersNames;
  bool isFaved;
  FavedPostDetails({
    this.favesTotalNumber = 0,
    @required this.favedUsersNames,
    @required this.isFaved,
  });
}

///Class PostDetails includes complete information about the post : its id, instance of PicPosterDetails, instance of FavedPostdetails,
///total number of comments on post, the image posted, caption (if available) and since when was it posted.
class PostDetails with ChangeNotifier {
  String id;
  PicPosterDetails picPoster;
  //int favesTotalNumber;
  FavedPostDetails favesDetails;
  int commentsTotalNumber;
  Map<String, String> lastComment;
  String postImageUrl;
  String caption;
  String postedSince;
  String description;
  bool privacy;
  DateTime dateTaken;
  String tags;

  PostDetails({
    @required this.id,
    @required this.picPoster,
    //@required this.favesTotalNumber,
    @required this.commentsTotalNumber,
    @required this.postImageUrl,
    this.lastComment,
    this.caption,
    @required this.postedSince,
    @required this.favesDetails,
    @required this.dateTaken,
    @required this.description,
    @required this.privacy,
    @required this.tags,
  });

  ///Reflects the user action when he clicks the fave button on the screen as well as updates the database.
  void toggleFavoriteStatus() {
    favesDetails.isFaved = !favesDetails.isFaved;
    if (favesDetails.isFaved) {
      favesDetails.favesTotalNumber += 1;
      favesDetails.favedUsersNames.insert(0, "You");
    } else {
      favesDetails.favesTotalNumber -= 1;
      favesDetails.favedUsersNames.remove("You");
    }
    notifyListeners();
    updateFavoriteStatus(favesDetails.isFaved, favesDetails.favesTotalNumber);
  }

  ///UpdateFavoriteStatus is called inside toggleFavoriteStatus function to reflect changes on database.
  Future<void> updateFavoriteStatus(bool isFaved, int favesTotalNumber) async {
    /* final url = Uri.https(
        'flickr-explore-default-rtdb.firebaseio.com', '/ExplorePosts/$id.json'); */
    final url =
        Uri.http(globals.HttpSingleton().getBaseUrl(), '/Explore_posts/$id');
    print(url);
    print(isFaved);
    print(favesTotalNumber);
    try {
      await http.patch(
        url,
        headers: {
          "Content-Type": "application/json",
        },
        body: json.encode(
          {
            'isFaved': isFaved,
            'favesTotalNumber': favesTotalNumber,
          },
        ),
      );
    } catch (error) {
      throw (error);
    }
  }

  ///Reflects the user action on screen as well as the data base if he chooses to follow the owner of the post
  ///by clicking on the pop menu button and then follow.
  void followPicPoster(List<PostDetails> posts) {
    picPoster.isFollowedByUser = true;
    picPoster.followedDuringRunning = true;

    notifyListeners();
    updateFollowPicPoster(posts);
  }

  void toggleFollowPicPoster(
      List<PostDetails> posts, PicPosterDetails personDetails) {
    personDetails.isFollowedByUser = !personDetails.isFollowedByUser;

    posts.forEach((post) {
      if (post.picPoster.profileId == personDetails.profileId) {
        post.picPoster.isFollowedByUser = !post.picPoster.isFollowedByUser;
      }
    });

    picPoster.isFollowedByUser = !picPoster.isFollowedByUser;
    //picPoster.followedDuringRunning = true;
    personDetails.notify();
    notifyListeners();
    updateFollowPicPoster(posts);
  }

  ///This function is called inside followPicPoster to reflect change on database.
  Future<void> updateFollowPicPoster(List<PostDetails> posts) async {
    /* final url = Uri.https(
        'flickr-explore-default-rtdb.firebaseio.com', '/ExplorePosts/$id.json'); */
    //print(Posts().posts.length);
    final loopList = posts
        .where((post) => post.picPoster.profileId == picPoster.profileId)
        .toList();

    print(loopList.length);

    for (int idcounter = 0; idcounter < loopList.length; idcounter++) {
      final url = Uri.http(globals.HttpSingleton().getBaseUrl(),
          '/Explore_posts/${loopList[idcounter].id}');
      print(url);
      await http.patch(
        url,
        headers: {
          "Content-Type": "application/json",
        },
        body: json.encode(
          {
            'isFollowedByUser': picPoster.isFollowedByUser,
          },
        ),
      );
    }
  }

  ///Returns the short list of the users names who faved the post to display on screen.
  List<String> get favedUsersNamesCopy {
    return [...favesDetails.favedUsersNames];
  }
}
