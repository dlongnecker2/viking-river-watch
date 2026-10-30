/* Independent family journey view. Existing river, weather and ship scripts are unchanged. */
(function(){
"use strict";
const stops=[
["2026-10-31","Flight to Europe"],["2026-11-01","Amsterdam"],["2026-11-02","Amsterdam"],["2026-11-03","Amsterdam / embark"],["2026-11-04","Kinderdijk"],["2026-11-05","Cologne"],["2026-11-06","Middle Rhine (revised)"],["2026-11-07","Miltenberg"],["2026-11-08","Würzburg"],["2026-11-09","Bamberg"],["2026-11-10","Nuremberg"],["2026-11-11","Regensburg"],["2026-11-12","Passau"],["2026-11-13","Melk / Wachau"],["2026-11-14","Vienna"],["2026-11-15","Vienna"],["2026-11-16","Budapest"],["2026-11-17","Budapest"],["2026-11-18","Budapest"],["2026-11-19","Return flight"]
];
const tomorrowFacts={
"Amsterdam":["Historic canals and narrow canal houses make Amsterdam one of Europe's most recognizable cities.","Amsterdam"],
"Kinderdijk":["The UNESCO-listed windmills were built to help drain the Dutch lowlands.","Kinderdijk"],
"Cologne":["Cologne Cathedral took more than 600 years to complete and dominates the Rhine skyline.","Cologne_Cathedral"],
"Middle Rhine (revised)":["The Rhine Gorge is known for castles, vineyards and the Lorelei bend. Viking's revised routing may differ.","Upper_Middle_Rhine_Valley"],
"Miltenberg":["This Main River town is celebrated for its timber-framed historic center.","Miltenberg"],
"Würzburg":["The Würzburg Residence is a UNESCO-listed Baroque palace.","Würzburg_Residence"],
"Bamberg":["Bamberg's historic center is a UNESCO World Heritage Site.","Bamberg"],
"Nuremberg":["Nuremberg is known for its medieval castle and historic old town.","Nuremberg"],
"Regensburg":["The medieval Stone Bridge crosses the Danube at Regensburg.","Regensburg"],
"Passau":["Three rivers—the Danube, Inn and Ilz—meet in Passau.","Passau"],
"Melk / Wachau":["Melk Abbey stands high above the Danube in Austria's Wachau Valley.","Melk_Abbey"],
"Vienna":["Vienna is renowned for its imperial palaces and musical heritage.","Vienna"],
"Budapest":["The Hungarian Parliament is one of the city's best-known Danube landmarks.","Hungarian_Parliament_Building"]
};
const $=id=>document.getElementById(id);
const parts=new Intl.DateTimeFormat("en-CA",{timeZone:"Europe/Amsterdam",year:"numeric",month:"2-digit",day:"2-digit"}).formatToParts(new Date());
const p=Object.fromEntries(parts.map(x=>[x.type,x.value]));
const today=p.year+"-"+p.month+"-"+p.day;
const current=stops.findIndex(x=>x[0]===today);
const progress=today<stops[0][0]?0:today>stops[stops.length-1][0]?100:Math.round((current+1)/stops.length*100);
$("journey-progress-fill").style.width=progress+"%";
$("journey-progress-label").textContent=today<stops[0][0]?"Departing October 31":today>stops[stops.length-1][0]?"Journey complete":("Day "+(current+1)+" of "+stops.length);
$("journey-today").textContent=current>=0?stops[current][1]:today<stops[0][0]?"Amsterdam next":"Trip completed";
const routeCoordinates=[
[52.3676,4.9041],[52.3676,4.9041],[52.3676,4.9041],[52.3676,4.9041],[51.8853,4.6369],[50.9375,6.9603],[50.3569,7.5889],[49.7039,9.2644],[49.7913,9.9534],[49.8988,10.9028],[49.4521,11.0767],[49.0134,12.1016],[48.5667,13.4319],[48.2279,15.3319],[48.2082,16.3738],[48.2082,16.3738],[47.4979,19.0402],[47.4979,19.0402],[47.4979,19.0402],[47.4979,19.0402]
];
if(typeof L!=="undefined"&&$("family-route-map")){
 const m=L.map("family-route-map",{scrollWheelZoom:false}).setView([50,11],5);
 L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",{maxZoom:17,attribution:"&copy; OpenStreetMap contributors"}).addTo(m);
 const unique=[];
 stops.forEach((stop,i)=>{
  const coord=routeCoordinates[i];
  if(!unique.length||coord[0]!==unique[unique.length-1][0]||coord[1]!==unique[unique.length-1][1])unique.push(coord);
  if(i===0||i===19)return;
  const status=stop[0]<today?"Scheduled date passed":stop[0]===today?"Scheduled today":"Upcoming scheduled stop";
  L.circleMarker(coord,{radius:stop[0]===today?8:5,color:stop[0]<today?"#168447":stop[0]===today?"#267fc2":"#647b87",fillOpacity:1}).addTo(m).bindPopup("<strong>"+stop[1]+"</strong><br>"+status+" — "+stop[0]);
 });
 for(let i=1;i<unique.length;i++){
  const originalIndex=routeCoordinates.findIndex(c=>c[0]===unique[i][0]&&c[1]===unique[i][1]);
  L.polyline([unique[i-1],unique[i]],{color:stops[originalIndex][0]<today?"#168447":"#647b87",weight:4,dashArray:stops[originalIndex][0]<today?null:"7 7"}).addTo(m);
 }
 m.fitBounds(L.latLngBounds(unique),{padding:[22,22]});
}
const route=$("journey-route");
stops.forEach(([date,place])=>{
 const card=document.createElement("div");card.className="journey-stop "+(date<today?"past":date===today?"today":"future");
 const d=document.createElement("span");d.textContent=new Date(date+"T12:00:00Z").toLocaleDateString("en-US",{month:"short",day:"numeric",timeZone:"UTC"});
 const name=document.createElement("strong");name.textContent=place;
 card.append(d,name);route.append(card);
});
const next=stops.find(x=>x[0]>today);
if(next){
 const place=next[1].split(" / ")[0];const facts=tomorrowFacts[place]||["Check the Viking Daily for your confirmed plans.",null];
 const panel=$("journey-tomorrow");panel.replaceChildren();
 const h=document.createElement("h4");h.textContent=new Date(next[0]+"T12:00:00Z").toLocaleDateString("en-US",{month:"long",day:"numeric",timeZone:"UTC"})+" · "+next[1];
 const para=document.createElement("p");para.textContent=facts[0];panel.append(h,para);
 const note=document.createElement("p");note.className="travel-muted";note.textContent="Scheduled itinerary only; Viking's transfers and excursions may change. Check the Viking Daily for actual plans.";panel.append(note);
 if(facts[1])fetch("https://en.wikipedia.org/w/api.php?action=query&format=json&origin=*&prop=pageimages&piprop=thumbnail&pithumbsize=650&titles="+encodeURIComponent(facts[1])).then(r=>r.json()).then(data=>{
  const url=Object.values(data.query?.pages||{})[0]?.thumbnail?.source;if(!url)return;
  const img=document.createElement("img");img.className="journey-tomorrow-photo";img.src=url;img.alt=place;img.loading="lazy";panel.append(img);
 }).catch(()=>{});
}else $("journey-tomorrow").textContent="Our European adventure has concluded.";
$("journey-share").addEventListener("click",async()=>{
 const url=location.origin+location.pathname+"#family-journey-home";
 try{if(navigator.share)await navigator.share({title:"Follow our Viking journey",url});else{await navigator.clipboard.writeText(url);$("journey-share").textContent="Link copied!";}}catch(e){if(e.name!=="AbortError")prompt("Copy this family link:",url);}
});
Promise.allSettled([
 fetch("cruise-assignment.json?fresh="+Date.now(),{cache:"no-store"}).then(r=>r.ok?r.json():Promise.reject(Error("assignment"))),
 fetch("journey-postcards.json?fresh="+Date.now(),{cache:"no-store"}).then(r=>r.ok?r.json():Promise.reject(Error("postcards")))
]).then(([assignment,postcards])=>{
 if(assignment.status==="fulfilled"){
  const a=assignment.value;
  if(a.active_ship?.name)$("journey-ship").textContent=a.active_ship.name;
  if(Array.isArray(a.itinerary_overrides)){
   // Date-specific itinerary changes are displayed as revised, not inferred from AIS.
   a.itinerary_overrides.forEach(change=>{
    if(!change.date||!change.destination)return;
    const i=stops.findIndex(x=>x[0]===change.date);if(i<0)return;
    const card=route.children[i];if(card){card.querySelector("strong").textContent=change.destination+" (revised)";}
    if(change.date===today)$("journey-today").textContent=change.destination+" (revised)";
   });
  }
 }
 const panel=$("journey-postcards");panel.replaceChildren();
 const entries=postcards.status==="fulfilled"&&Array.isArray(postcards.value.entries)?postcards.value.entries:[];
 if(!entries.length){panel.textContent="No postcards shared yet. Check back after we arrive in Europe!";return;}
 entries.slice().sort((a,b)=>b.date.localeCompare(a.date)).forEach(entry=>{
  const card=document.createElement("article");card.className="journey-postcard";
  const h=document.createElement("h4");h.textContent=(entry.date||"")+" · "+(entry.place||"Our journey");card.append(h);
  if(entry.photo){const img=document.createElement("img");img.src=entry.photo;img.alt=entry.photo_alt||entry.place||"Trip photo";img.loading="lazy";card.append(img);}
  const para=document.createElement("p");para.textContent=entry.note||"";card.append(para);panel.append(card);
 });
});
})();