// Filter depending on category

var tr = document.getElementsByTagName("tr")
var btns = document.querySelectorAll(".btn-simple")
for (var i=0; i<btns.length; i++){
  btns[i].addEventListener("click", function(){
    for (j = 1; j < tr.length; j++) {
      var sentiment = tr[j].getElementsByTagName("td")[6].innerText.replace(/\s/g, '');
      console.log(sentiment)
      if (this.innerText === "All") {
         tr[j].style.display = "";
      }
      else if (this.innerText === sentiment) {
         tr[j].style.display = "";
      }
      else {
        tr[j].style.display = "none";
      }
    }
  })
}