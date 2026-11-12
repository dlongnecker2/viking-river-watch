/* Independent family journey view. Existing river, weather and ship scripts are unchanged. */
(function(){
"use strict";
const stops=[
["2026-10-31","Flight to Europe"],["2026-11-01","Amsterdam"],["2026-11-02","Amsterdam"],["2026-11-03","Amsterdam / embark"],["2026-11-04","Kinderdijk"],["2026-11-05","Cologne"],["2026-11-06","Frankfurt / Rhine Gorge boat & Koblenz"],["2026-11-07","Miltenberg"],["2026-11-08","Würzburg"],["2026-11-09","Bamberg"],["2026-11-10","Nuremberg / coach transfer to Viking Ve at Passau (completed)"],["2026-11-11","Regensburg"],["2026-11-12","Passau"],["2026-11-13","Melk / Wachau / Krems"],["2026-11-14","Vienna"],["2026-11-15","Vienna"],["2026-11-16","Budapest"],["2026-11-17","Budapest hotel check-in"],["2026-11-18","Budapest — booked 7 PM private night tour"],["2026-11-19","Budapest airport transfer and return flight"]
];
const tomorrowFacts={
"Budapest hotel check-in":["Hotel check-in at 3:00 PM. The Viking hospitality desk is in the lobby.","Budapest"],
"Budapest — booked 7 PM private night tour":["Our private night tour with Mary Carry runs 7:00–10:00 PM.","Budapest"],
"Budapest airport transfer and return flight":["Check out by 10:00 AM and confirm your personal airport transfer time at the hospitality desk.",null],
"Frankfurt / Rhine Gorge boat & Koblenz":["Viking Vidar arrives in Frankfurt at 7 AM. The 8 AM–5 PM excursion travels by coach to Bingen, then by smaller sightseeing boat through the Rhine Gorge to Koblenz, returning to Frankfurt by coach; all aboard at 7 PM.","Upper_Middle_Rhine_Valley"],
"Amsterdam":["Historic canals and narrow canal houses make Amsterdam one of Europe's most recognizable cities.","Amsterdam"],
"Kinderdijk":["The UNESCO-listed windmills were built to help drain the Dutch lowlands.","Kinderdijk"],
"Cologne":["Cologne Cathedral took more than 600 years to complete and dominates the Rhine skyline.","Cologne_Cathedral"],
"Middle Rhine (revised)":["The Rhine Gorge is known for castles, vineyards and the Lorelei bend. Viking's revised routing may differ.","Upper_Middle_Rhine_Valley"],
"Miltenberg":["Saturday, November 7: Viking Vidar is scheduled to arrive at 9:00 AM. Included Miltenberg walking tour 9:15–11:00 AM (bring charged QuietVox). All aboard by noon; ship departs shortly afterward for Würzburg. Sun Deck closed due to low bridge clearances.","Miltenberg"],
"Würzburg":["Sunday, November 8: Our booked excursion is Rothenburg ob der Tauber, 9:00 AM–5:30 PM (not the included Würzburg walking tour). Ten things to see and eat: 1) Plönlein, 2) Marktplatz and Town Hall, 3) Schneeball pastry, 4) medieval town walls, 5) St. Jakob’s Church, 6) Käthe Wohlfahrt Christmas Village, 7) Franconian bratwurst, 8) Burggarten viewpoint, 9) apple strudel, 10) Medieval Crime Museum if time permits. Viking Vidar arrives Würzburg at 7:00 AM and plans to depart for Bamberg after 5:30 PM. Follow the Viking guide for return transport; tour ends at all-aboard time.","Rothenburg_ob_der_Tauber"],
"Bamberg":["Monday November 9: Viking Vidar is scheduled to arrive around 2 PM. Our booked INCLUDED Bamberg Walking Tour 2–5:30 PM (not the optional Franconian Beer Culture excursion) (approximately 5-minute bus ride). Bring charged QuietVox. All aboard 6 PM; sail toward Nuremberg shortly afterward. Top sights and tastes: Altes Rathaus on the Regnitz, Bamberg Cathedral, Little Venice, Old Court, New Residence, Rose Garden, smoked Rauchbier, Franconian bratwurst, traditional bakeries and scenic old-town lanes.","Bamberg"],
"Nuremberg":["Tuesday Nov 10: Viking Vidar arrives Nuremberg at 8 AM. Put luggage outside your stateroom before 8:30 AM. Excursions begin at 8:30 AM; included Nuremberg Through History ends at noon (follow your excursion ticket). Group lunch at Heilig Geist Spital 12:00–1:15 PM. Meet the transfer bus at Augustinerstrasse; be aboard by 1:30 PM. Coach to Viking Ve at Passau Lindau (approx. 230 km / 145 miles), arriving around 4:30 PM. Keep valuables and medication with you, take QuietVox receiver and earpiece, and leave the charger. On Viking Ve: welcome drinks 5:45–6:30 PM, captain’s toast 6:30 PM, restaurant dinner 7 PM, music 9 PM. Ship swap completed; passenger confirms aboard Viking Ve at Passau.","Nuremberg"],
"Regensburg":["The medieval Stone Bridge crosses the Danube at Regensburg.","Regensburg"],
"Passau":["Three rivers—the Danube, Inn and Ilz—meet in Passau.","Passau"],
"Melk / Wachau / Krems":["Viking Ve is scheduled to reach Melk at 8:30 AM. Our Melk Abbey and Organ Concert tour runs 9:15–11:30 AM. Scenic sailing begins at 1:45 PM, with arrival in Krems at 4:00 PM and departure for Vienna at 9:45 PM.","Melk_Abbey"],
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
[52.3676,4.9041],[52.3676,4.9041],[52.3676,4.9041],[52.3676,4.9041],[51.8853,4.6369],[50.9375,6.9603],[50.1109,8.6821],[49.7039,9.2644],[49.7913,9.9534],[49.8988,10.9028],[49.4521,11.0767],[49.0134,12.1016],[48.5667,13.4319],[48.2279,15.3319],[48.2082,16.3738],[48.2082,16.3738],[47.4979,19.0402],[47.4979,19.0402],[47.4979,19.0402],[47.4979,19.0402]
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
 const place=next[1].split(" / ")[0];const facts=tomorrowFacts[next[1]]||tomorrowFacts[place]||["Check the Viking Daily for your confirmed plans.",null];
 const panel=$("journey-tomorrow");panel.replaceChildren();
 const h=document.createElement("h4");h.textContent=new Date(next[0]+"T12:00:00Z").toLocaleDateString("en-US",{month:"long",day:"numeric",timeZone:"UTC"})+" · "+next[1];
 const para=document.createElement("p");para.textContent=facts[0];panel.append(h,para);
 if(next[0]==="2026-11-13"){const link=document.createElement("a");link.href="#viking-daily-nov13";link.textContent="Full Viking Daily schedule";panel.append(link);}
 if(next[0]>="2026-11-17" && next[0]<="2026-11-19"){const link=document.createElement("a");link.href="#budapest-extension";link.textContent="Full Budapest hotel extension schedule";panel.append(link);}
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
  if(a.scheduled_ship?.name&&a.scheduled_ship.effective_date<=today)$("journey-ship").textContent=a.scheduled_ship.name;else if(a.active_ship?.name)$("journey-ship").textContent=a.active_ship.name;
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
  const pictures=Array.isArray(entry.photos)&&entry.photos.length?entry.photos:(entry.photo?[entry.photo]:[]);for(const picture of pictures){
   const img=document.createElement("img");
   img.alt=entry.photo_alt||entry.place||"Trip photo";
   img.loading="eager";
   img.decoding="async";
   img.style.display="block";
   img.style.minHeight="120px";
   const safeName=picture.startsWith("/") ? picture.slice(1) : picture;
   const localURL=new URL(safeName,document.baseURI).href;
   const fallbackURL="https://raw.githubusercontent.com/dlongnecker2/viking-river-watch/main/"+safeName.split("/").map(encodeURIComponent).join("/");
   let triedFallback=false;
   img.onerror=()=>{
    if(!triedFallback){triedFallback=true;img.src=fallbackURL;return;}
    img.style.display="none";
    const warning=document.createElement("p");warning.className="travel-muted";
    warning.textContent="Photo temporarily unavailable: "+safeName;
    const link=document.createElement("a");link.href=fallbackURL;link.textContent="Open photo";link.target="_blank";link.rel="noopener noreferrer";
    warning.append(" · ",link);card.insertBefore(warning,img.nextSibling);
   };
   img.src=localURL;
   card.append(img);
  }
  const para=document.createElement("p");para.textContent=entry.note||"";card.append(para);panel.append(card);
 });
});
})();