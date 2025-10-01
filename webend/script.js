var searchIndex={
	"statName":{},
	"players":{}
}
document.addEventListener("DOMContentLoaded", function() {
	
	// Function to add list items to #listContainer
	function addListItem(name, total, max, min) {
		const listItem = document.createElement("li");
		listItem.innerHTML = `
	<stat title="Go to Full Leaderboard of '${name.replaceAll("_"," ").replaceAll("."," ")}'" onclick="if(event.target.closest('a')) return; window.open('stat/${name}.html','_blank');" >
	<strong class=stathead >${name}</strong>
	<div class="total"><div>
	
		Total: ${total}
	</div></div>
	<div class="players">
		<div class="minimax max">
			<span>Max: ${max.amount}</span>
			<div class=inline>
				${max.players.map(player => `<span class="player"><a class='profile_link' href='player/${player}.html' target="_blank"><img class='inline_face' src='faces/${player}.png'>${player}</a></span>`).join(", ")}
			</div> 
		</div>
		<hr/>
		<div class="minimax min">
			<span>Min: ${min.amount}</span>
			<div  class=inline>
			${min.players.map(player => `<span class="player"><a class='profile_link' href='player/${player}.html' target="_blank"><img class='inline_face' src='faces/${player}.png'>${player}</a></span>`).join(", ")}
			</div> 
		</div> 
	</div>
	</stat>
	`;
		listContainer.appendChild(listItem);
		return(listItem)
	}

	const filterInput = document.getElementById("searchInput");
	const listContainer = document.getElementById("listContainer");

	// Function to filter the list items based on the input value
	let searchID = 0
	async function filterListItemsAsync() {
		// Clear the previous timeout if there was one
		searchID++
		let myID = searchID
		const statfilter = document.getElementById("filterStat").checked;
		const maxfilter = document.getElementById("filterMax").checked;
		const minfilter = document.getElementById("filterMin").checked;
		//console.log(statfilter, maxfilter, minfilter)
		// Wrap the function logic in a Promise to handle asynchronous operations
		// Set a new timeout to wait for a brief moment of inactivity in input events

		const filterValue = filterInput.value.toLowerCase().replaceAll("_", " ").replaceAll(".", " ");
		const listItems = listContainer.getElementsByTagName("li");
		const markedItems = listContainer.getElementsByClassName("match");
		//console.log(filterValue)
	
		let counter = 0;
		await new Promise(resolve => setTimeout(resolve, 1));//let the ui update
		for (const markedItem of markedItems) {
			counter++
			if (counter % 100 == 0) {
				await new Promise(resolve => setTimeout(resolve, 1));
				counter=0
			}
			if (myID != searchID) {
				break
			}
			markedItem.classList.remove("match");
			
		}
		await new Promise(resolve => setTimeout(resolve, 1));//let the ui update
		for (const listItem of listItems) {
			counter++
			if (counter % 100 == 0) {
				await new Promise(resolve => setTimeout(resolve, 1));
				counter=0
			}
			if (myID != searchID) {
				break
			}
			
			if (filterValue === "") {
				foundMatch = listItem.style.display="block";
				
			} else {
				foundMatch = listItem.style.display="none";
			}
			
		}
		
		await new Promise(resolve => setTimeout(resolve, 1));//let the ui update
		if(statfilter){
			for (const name in searchIndex.statName) {
				counter++
				if (counter % 100 == 0) {
					await new Promise(resolve => setTimeout(resolve, 1));
					counter=0
				}
				if (myID != searchID) {
					break
				}
				if(name.includes(filterValue)){
					searchIndex.statName[name].style.display="block";
					if(filterValue!=""){
						searchIndex.statName[name].getElementsByClassName("stathead")[0].classList.add("match");
					}
				}
			}
		}
		await new Promise(resolve => setTimeout(resolve, 1));//let the ui update
		if(maxfilter || minfilter){
			for (const name in searchIndex.players) {
				counter++
				if (counter % 100 == 0) {
					await new Promise(resolve => setTimeout(resolve, 1));
					counter=0
				}
				if (myID != searchID) {
					break
				}
				if(name.includes(filterValue)){
					if(maxfilter){
						for(const li of searchIndex.players[name].max){
							li.style.display="block";

							const matched = li.querySelectorAll("div.minimax.max .player");

							matched.forEach(el => {
									
								if(el.textContent.toLowerCase().includes(filterValue)){
									el.classList.add("match")
								}
							});
						
						}
						
					}
					if(minfilter){
						for(const li of searchIndex.players[name].min){
							li.style.display="block";
							
								const matched = li.querySelectorAll("div.minimax.min .player");
								matched.forEach(el => {
									if(el.textContent.toLowerCase().includes(filterValue)){
										el.classList.add("match")
									}
								});
							
						}
						
					}
				}
			}
		}
	}

	const cacheKey = $(location).prop("href").split("/").slice(-4,-2).join("/")+"/leaderboard.json";
	localStorage.removeItem('cachedJSONData');
	async function loadJSONData() {
		var dataversion = 0
		try {
			const response = await fetch('dataversion'); // Replace with the actual relative path
			dataversion = await response.text();
			//console.log("dataversion: ",dataversion);
		} catch (error) {
			console.error('Error fetching dataversion file:', error);
			throw new error(error)
		}

		return new Promise((resolve, reject) => {
			// Check if the JSON data is already cached
			const cachedData = localStorage.getItem(cacheKey);

			const existingDataversion = getCookie('dataversion');
			//console.log("existingDataversion: ",existingDataversion);
			//console.log("dataversion: ",dataversion);
			if (existingDataversion && existingDataversion === dataversion && cachedData) {
				// If data is cached, parse and resolve the promise
				const jsonData = JSON.parse(cachedData);
				resolve(jsonData);
			} else {
				// If data is not cached, make a fetch request and cache the data
				fetch("leaderboard.json")
					.then(response => response.json())
					.then(data => {
						try{
							// Cache the data in localStorage
							localStorage.setItem(cacheKey, JSON.stringify(data));
						}catch(error){
							console.error(error)
							console.error("Clearing cache and retrying")
							localStorage.clear()
							localStorage.setItem(cacheKey, JSON.stringify(data));
						}
						resolve(data);
						setCookie('dataversion', dataversion);
					})
					.catch(error => reject(error));
			}
		});
	}

	// Load the JSON data and add list items asynchronously
	async function processJSON(data) {
		let counter=0;
		for (const entry of data) {
			//counter++
			//if (counter % 100 == 0) {
			//	await new Promise(resolve => setTimeout(resolve, 0));
			//	counter=0
			//}
			counter++
			if (counter % 100 == 0) {
				await new Promise(resolve => setTimeout(resolve, 1));
				counter=0
			}
			if(entry.name=='minecraft.crafted.air'){
				continue
			}
			const item=addListItem(entry.name, entry.total, entry.max, entry.min);
			
			searchIndex.statName[entry.name.replaceAll("_", " ").replaceAll(".", " ")]=item
			//console.log(entry)
			for(const raw of entry.max.players){
				
				const name=raw.toLowerCase().replaceAll("_", " ").replaceAll(".", " ")
				if(! (name in searchIndex.players)){
						searchIndex.players[name]={"max":[],"min":[]};
				}
				//console.log(name,searchIndex.players[name])
				searchIndex.players[name].max.push(item)
			}
			for(const raw of entry.min.players){
				const name=raw.toLowerCase().replaceAll("_", " ").replaceAll(".", " ")
				if(! (name in searchIndex.players)){
						searchIndex.players[name]={"max":[],"min":[]};
				}
				searchIndex.players[name].min.push(item)
			}
		}
	}
	loadJSONData()
		.then(data => {
			processJSON(data);

		})
		.catch(error => console.error("Error loading JSON data:", error));
	filterInput.addEventListener("input", async () => {
		await filterListItemsAsync();
	});
	document.getElementById('filterMax').addEventListener("input", async () => {
		await filterListItemsAsync();
	});
	document.getElementById('filterStat').addEventListener("input", async () => {
		await filterListItemsAsync();
	});
	document.getElementById('filterMin').addEventListener("input", async () => {
		await filterListItemsAsync();
	});
	
});

function topFunction() {
	document.body.scrollTop = 0; // For Safari
	document.documentElement.scrollTop = 0; // For Chrome, Firefox, IE and Opera
}
// Function to get the value of a cookie
function getCookie(cookieName) {
	const cookies = document.cookie.split('; ');
	for (const cookie of cookies) {
		const [name, value] = cookie.split('=');
		if (name === cookieName) {
			return value;
		}
	}
	return null;
}

// Function to set the value of a cookie
function setCookie(cookieName, value) {
	document.cookie = `${cookieName}=${value}`;
	
}

const initialDarkCookie=localStorage.getItem('darkmode')
if(initialDarkCookie=='sane'){
		activateLightMode();
		document.getElementById('saneMode').checked=true;
	}else if(initialDarkCookie=='dark'){
		activateDarkMode();
		document.getElementById('darkMode').checked=true;
	}else if(initialDarkCookie=='amoled'){
		activateAmoledMode();
		document.getElementById('amoledMode').checked=true;
	}
function activateLightMode(){
	const rootElement = document.documentElement;
	rootElement.removeAttribute('class');
	localStorage.setItem('darkmode','sane');
}

function activateDarkMode(){
	const rootElement = document.documentElement;
	rootElement.removeAttribute('class');
	rootElement.classList.add('darkmode');
	localStorage.setItem('darkmode','dark')
}

function activateAmoledMode(){
		const rootElement = document.documentElement;
	rootElement.removeAttribute('class');
	rootElement.classList.add('amoledmode');
	localStorage.setItem('darkmode','amoled')
}
