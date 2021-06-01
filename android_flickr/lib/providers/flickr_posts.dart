//import 'package:android_flickr/providers/flickr_profiles.dart';

import 'package:intl/intl.dart';

import './flickr_post.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:flutter/foundation.dart';
import '../Classes/globals_moaz.dart' as globals;

///Class Posts is used to obtain lists of class post in order to display these posts on our explore screen.
class Posts with ChangeNotifier {
  List<PostDetails> _posts = [];
  List<PostDetails> _myPosts = [];

  /* Future<void> _addPostsToDatabase() async {
    final url = Uri.https(
        'https://flickr-explore-default-rtdb.firebaseio.com', '/posts.json');
    await http.post(
      url,
      body: json.encode(
        {
          'commentsTotalNumber': 80,
          'lastComment': {
            'Ahmed elghandoor': 'what a great picture!,lets enjoy this weather',
          },
          'postImageUrl':
              'assets/images/GetStartedScreens/GetStartedScreenSlide1.png',
          'postedSince': '6d',
          'caption': "nice weather",
          'favesDetails': {
            'favesTotalNumber': [],
            'favedUsersNames': [],
            'bool isFaved': []
          },
          'PicPosterDetails': {
            'name': [],
            'isPro': [],
            'isFollowedByUser': [],
            'profilePicUrl': [],
          }
        },
      ),
    );
  } */

  ///Used to fetch data from the firebase database and set them in the List of posts.
  Future<void> fetchAndSetExplorePosts() async {
    /* final url = Uri.https(
        'flickr-explore-default-rtdb.firebaseio.com', '/ExplorePosts.json'); */
    //const url = 'https://flutter-update.firebaseio.com.json';
    fetchAndSetMyPosts();
    final url =
        Uri.http(globals.HttpSingleton().getBaseUrl(), '/Explore_posts');
    //print(url);

    try {
      final response = await http.get(url);
      //print(response.body);
      /* final extractedData =
          json.decode(response.body) as List<Map<String, dynamic>>; */
      final extractedData = json.decode(response.body) as List<dynamic>;
      //print(extractedData);
      final List<PostDetails> loadedPosts = [];
      final List<String> loadedProfilesId = [];
      extractedData.forEach(
        (postDetails) {
          if (!loadedProfilesId.contains(
            postDetails['ProfileId'].toString(),
          )) {
            loadedProfilesId.add(postDetails['ProfileId'].toString());
          }

          int postUrl = postDetails['id'] * 2;
          //print(postUrl);
          /* String postUrl = 'https://picsum.photos/200/200?random=' +
              '${postDetails['id'] + 5}'; */
          //print(postDetailsId);
          loadedPosts.add(
            PostDetails(
              id: postDetails['id'].toString(),
              commentsTotalNumber: postDetails['commentsTotalNumber'],
              favesDetails: FavedPostDetails(
                favedUsersNames: postDetails['isFaved']
                    ? [
                        'You',
                        postDetails['favedUsersNames1'],
                        postDetails['favedUsersNames2'],
                      ]
                    : [
                        postDetails['favedUsersNames1'],
                        postDetails['favedUsersNames2'],
                      ],
                isFaved: postDetails['isFaved'],
                favesTotalNumber: postDetails['favesTotalNumber'],
              ),
              picPoster: PicPosterDetails(
                postDetails['ProfileId'].toString(),
                postDetails['PicPosterDetailsname'],
                postDetails['isPro'],
                postDetails['isFollowedByUser'],
                'https://picsum.photos/200/200?random=' +
                    '${postDetails['ProfileId']}',
              ),
              postImageUrl:
                  'https://picsum.photos/200/200?random=' + '$postUrl',
              postedSince: postDetails['postedSince'],
              caption: postDetails['caption'],
              lastComment: {
                postDetails['lastCommentUser']: postDetails['lastCommentText'],
              },
              tags: postDetails['tags'],
              //dateTaken: postDetails['date_taken'],
              description: postDetails['description'],
              privacy: postDetails['privacy'],
              dateTaken:
                  DateFormat('dd-MMM-yyyy').parse(postDetails['date_taken']),
            ),
          );
        },
      );
      //print(loadedProfilesId.length);
      _posts = loadedPosts;
      //FlickrProfiles.profilesId = loadedProfilesId;
      //print(loadedProfiles[1].profileName);
      //print(loadedProfiles[51].profileID);
      notifyListeners();
    } catch (error) {
      print("error");
      //print('https://picsum.photos/200/200?random=' + '$postUrl');
      throw (error);
    }
  }

  ///Used to fetch data from the firebase database and set them in the List of posts.
  Future<void> fetchAndSetMyPosts() async {
    /* final url = Uri.https(
        'flickr-explore-default-rtdb.firebaseio.com', '/ExplorePosts.json'); */
    //const url = 'https://flutter-update.firebaseio.com.json';
    final url = Uri.http(globals.HttpSingleton().getBaseUrl(), '/MyPosts');
    //print(url);

    try {
      final response = await http.get(url);
      //print(response.body);
      /* final extractedData =
          json.decode(response.body) as List<Map<String, dynamic>>; */
      final extractedData = json.decode(response.body) as List<dynamic>;
      //print(extractedData);
      final List<PostDetails> loadedPosts = [];
      //final List<String> loadedProfilesId = [];
      extractedData.forEach(
        (postDetails) {
          /*  if (!loadedProfilesId.contains(
            postDetails['ProfileId'].toString(),
          )) {
            loadedProfilesId.add(postDetails['ProfileId'].toString());
          } */

          int postUrl = postDetails['id'] * 2;
          //print(postUrl);
          /* String postUrl = 'https://picsum.photos/200/200?random=' +
              '${postDetails['id'] + 5}'; */
          //print(postDetailsId);
          loadedPosts.add(
            PostDetails(
              id: postDetails['id'].toString(),
              commentsTotalNumber: postDetails['commentsTotalNumber'],
              favesDetails: FavedPostDetails(
                favedUsersNames: postDetails['isFaved']
                    ? [
                        'You',
                        postDetails['favedUsersNames1'],
                        postDetails['favedUsersNames2'],
                      ]
                    : [
                        postDetails['favedUsersNames1'],
                        postDetails['favedUsersNames2'],
                      ],
                isFaved: postDetails['isFaved'],
                favesTotalNumber: postDetails['favesTotalNumber'],
              ),
              picPoster: PicPosterDetails(
                "619",
                "Dragon Slayer",
                false,
                true,
                'https://picsum.photos/200/200?random=' +
                    '${619}',
              ),
              postImageUrl:
                  'https://picsum.photos/200/200?random=' + '$postUrl',
              postedSince: postDetails['postedSince'],
              caption: postDetails['caption'],
              lastComment: {
                postDetails['lastCommentUser']: postDetails['lastCommentText'],
              },
              tags: postDetails['tags'],
              //dateTaken: postDetails['date_taken'],
              description: postDetails['description'],
              privacy: postDetails['privacy'],
              dateTaken:
                  DateFormat('dd-MMM-yyyy').parse(postDetails['date_taken']),
            ),
          );
        },
      );
      //print(loadedProfilesId.length);
      _myPosts = loadedPosts;
      print(_myPosts.length);

      //FlickrProfiles.profilesId = loadedProfilesId;
      //print(loadedProfiles[1].profileName);
      //print(loadedProfiles[51].profileID);
      notifyListeners();
    } catch (error) {
      print("error");
      //print('https://picsum.photos/200/200?random=' + '$postUrl');
      throw (error);
    }
  }

  ///Returns copy of the List of posts.
  List<PostDetails> get posts {
    //print(_posts);
    return [..._posts];
  }
  List<PostDetails> get myPosts {
    //print(_posts);
    return [..._myPosts];
  }
}
