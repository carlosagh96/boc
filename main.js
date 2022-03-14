var prevScrollpos = window.pageYOffset;
window.onscroll = function()
{
var currentScrollPos = window.pageYOffset;
if (prevScrollpos > currentScrollPos) {
document.getElementById("this").style.top = "0";
}
else
{
document.getElementById("this").style.top = "-64px";
}
prevScrollpos = currentScrollPos;
}
