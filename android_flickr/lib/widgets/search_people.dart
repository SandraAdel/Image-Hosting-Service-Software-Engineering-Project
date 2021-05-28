import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/flickr_posts.dart';
import '../providers/flickr_post.dart';
import '../screens/non_profile_screen.dart';

class SearchPeople extends StatefulWidget {
  @override
  _SearchPeopleState createState() => _SearchPeopleState();
}

class _SearchPeopleState extends State<SearchPeople> {
  void _goToNonprofile(BuildContext ctx, PostDetails postInformation) {
    Navigator.of(ctx).pushNamed(
      NonProfileScreen.routeName,
      arguments: postInformation,
    );
  }

  @override
  Widget build(BuildContext context) {
    final peopleSearchDetails = Provider.of<Posts>(context).posts;
    return ListView.builder(
      itemCount: peopleSearchDetails.length,
      itemBuilder: (ctx, index) {
        return ListTile(
            leading: GestureDetector(
              onTap: () {
                _goToNonprofile(context, peopleSearchDetails[index]);
              },
              child: CircleAvatar(
                radius: MediaQuery.of(context).size.width / 20,
                backgroundImage: NetworkImage(
                  peopleSearchDetails[index].picPoster.profilePicUrl,
                ),
                backgroundColor: Colors.transparent,
                /* child: Image.asset(
                  postInformation.url,
                  alignment: Alignment.center,
                  fit: BoxFit.fill,

                  //height: double.infinity,
                ), */
              ),
            ),
            title: Text(
              peopleSearchDetails[index].picPoster.name,
              style: TextStyle(
                fontWeight: FontWeight.bold,
              ),
            ),
            subtitle: Text(
              "${500}" + " photos - " + "${500}" + " followers",
              overflow: TextOverflow.fade,
              softWrap: true,
            ),
            trailing: FlatButton(
              shape: Border.all(
                color: Colors.black,
                width: 2,
              ),
              color: Colors.transparent,
              onPressed: () {
                setState(() {
                  peopleSearchDetails[index].toggleFollowPicPoster();
                });
              },
              child: peopleSearchDetails[index].picPoster.isFollowedByUser
                  ? Icon(Icons.beenhere_outlined)
                  : Text("+" + " Follow"),
            ));
      },
    );
  }
}
