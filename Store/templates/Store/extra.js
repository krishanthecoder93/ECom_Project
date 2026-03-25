document.addEventListener("DOMContentLoaded", function(){

console.log("Sanity check!");

fetch("/config/")
.then(result => result.json())
.then(data => {

const stripe = Stripe(data.publicKey);

const btn = document.querySelector("#submitBtn");

if(btn){

btn.addEventListener("click", function(){
console.log("BUTTON CLICKED");
var txtadr = document.getElementById("txtadr").value;
var txtcty = document.getElementById("txtcty").value;
var txtsta = document.getElementById("txtsta").value;
var txtzipcod = document.getElementById("txtzipcod").value;

var totval = txtadr + "|" + txtcty + "|" + txtsta + "|" + txtzipcod;
console.log("totval");
console.log(totval);
;

fetch("/create-checkout-session/")
.then(result => result.json())
.then(data => {

console.log(data);

return stripe.redirectToCheckout({
sessionId: data.sessionId
});

});

});

}else{

console.log("submitBtn not found");

}

});

});