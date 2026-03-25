document.addEventListener("DOMContentLoaded", function(){
console.log("Sanity check!");


// new
// Get Stripe publishable key
fetch("/config/")
.then((result) => { return result.json(); })
.then((data) => {
  // Initialize Stripe.js
  const stripe = Stripe(data.publicKey);


// new
  // Event handler
  document.querySelector("#submitBtn").addEventListener("click", () => {
    // Get Checkout Session ID
    var txtadr =document.getElementById("txtadr").value;
    var txtcty =document.getElementById("txtcty").value;
    var txtsta =document.getElementById("txtsta").value;
    var txtzipcod =document.getElementById("txtzipcod").value;


    var totval =txtadr +"|"+ txtcty +"|"+ txtsta + "|"+txtzipcod;
    console.log(totval);

    fetch("/create-checkout-session/?query="+totval)
    .then((result) => { return result.json(); })
    .then((data) => {
      console.log(data);
      // Redirect to Stripe Checkout
      return stripe.redirectToCheckout({sessionId: data.sessionId})
    })
    .then((res) => {
      console.log(res);
    });
  });
});
});