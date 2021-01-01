// Search for selected tweets and save them into the "replies" Array

var replies = []
$("tr").on("click", "input", function(){
        var tweet_ID = $(this).closest('tr').find("td").eq(1).text().replace(/\s/g, '');
        if (($(this).closest('tr').find("td").eq(0).find('input').prop("checked") == true) && replies.includes(tweet_ID) == false )  {
          replies.push(tweet_ID);
          console.log(replies);
          }
        else if (($(this).closest('tr').find("td").eq(0).find('input').prop("checked") == false) && replies.includes(tweet_ID) == true ) {
          replies.splice(replies.indexOf(tweet_ID),1);
          console.log(replies);
        }
        })

// Send the tweet selected to Django view

/* data = {"tweets_selected": replies}
var url = "{% url 'main_app:testjs' %}"  */

//POST REQUEST
/* $("#send").on("click", function(){
    $.ajax({
        url: "http://127.0.0.1:8000/reply/testjs/",
        type: "POST",
        data: data,
        success:function(response){},
        complete:function(){},
        error:function (xhr, textStatus, thrownError){}
    });
}) */

//GET REQUEST
const url = "http://127.0.0.1:8000/reply/testjs/"
$("#send").on("click", function(){
  var created = {{created}};
  fetch(url).then(response => response.json()).then(data => console.log(data))
})