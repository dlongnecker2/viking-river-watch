"use strict";
// This is a public static file. Never store passwords or GitHub tokens here.
// Set the URL only after the secure server-side uploader is deployed.
const API_URL="";
const form=document.getElementById("form"),status=document.getElementById("status"),button=document.getElementById("publish"),photo=document.getElementById("photo"),preview=document.getElementById("preview");
document.getElementById("date").value=new Date().toLocaleDateString("en-CA");
photo.addEventListener("change",()=>{const file=photo.files[0];if(file){preview.src=URL.createObjectURL(file);preview.hidden=false;}});
form.addEventListener("submit",async e=>{e.preventDefault();if(!API_URL){status.textContent="Publishing is not connected yet. Secure server setup is required.";return;}const file=photo.files[0];if(!file||file.size>5*1024*1024){status.textContent="Choose an image smaller than 5 MB.";return;}button.disabled=true;status.textContent="Publishing…";try{const data=new FormData();for(const id of ["date","place","note","password"])data.append(id,document.getElementById(id).value);data.append("photo",file);const r=await fetch(API_URL,{method:"POST",body:data});if(!r.ok)throw Error("Upload failed ("+r.status+").");status.textContent="Postcard published! It may take a few minutes to appear.";form.reset();preview.hidden=true;}catch(err){status.textContent=err.message;}finally{button.disabled=false;}});
