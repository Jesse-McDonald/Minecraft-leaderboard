var searchIndex = {
	statName: {},
	players: {}
};

let visibleItems = new Set();

function sortList(ulElement, mode) {
	const items = Array.from(ulElement.children);

	if (mode === "random") {
		for (let i = items.length - 1; i > 0; i--) {
			const j = Math.floor(Math.random() * (i + 1));
			[items[i], items[j]] = [items[j], items[i]];
		}
	} else if (mode === "alpha" || mode === "rev-alpha") {
		items.sort((a, b) => {
			const cmp = a._search.stat.localeCompare(b._search.stat, undefined, { sensitivity: 'base' });
			return mode === "alpha" ? cmp : -cmp;
		});
	} else if (mode === "numeric" || mode === "rev-numeric") {
		items.sort((a, b) => {
			return mode === "numeric" ? (a._total - b._total) : (b._total - a._total);
		});
	}

	items.forEach(item => ulElement.appendChild(item));
}

function match(filterValue, statfilter, maxfilter, minfilter,li){
	const data = li._search;

		

		if (statfilter && data.stat.includes(filterValue)) {
			return true;
		}

		if (maxfilter) {
			for (const p of data.max) {
				if (p.includes(filterValue)) {
					return  true;
					
				}
			}
		}

		if (minfilter) {
			for (const p of data.min) {
				if (p.includes(filterValue)) {
					return true;
		
				}
			}
		}
		return false
		
}
function computeMatches(filterValue, statfilter, maxfilter, minfilter, listContainer) {
	const matches = new Set();

	for (const li of listContainer.children) {
		if (filterValue){
			if( match(filterValue, statfilter, maxfilter, minfilter,li)){
				matches.add(li);
			}
		}else{
			matches.add(li);
		}
	}

	return matches;
}

function applyVisibility(matches) {
	requestAnimationFrame(() => {
		for (const el of visibleItems) {
			if (!matches.has(el)) el.classList.add("hidden");
		}
		for (const el of matches) {
			if (!visibleItems.has(el)) el.classList.remove("hidden");
		}
		visibleItems = matches;
	});
}

document.addEventListener("DOMContentLoaded", function () {
	const filterInput = document.getElementById("searchInput");
	const listContainer = document.getElementById("listContainer");

	document.getElementById('shuffle').addEventListener("click", () => {
		sortList(listContainer, "random");
	});

	document.getElementById('sortSelect').addEventListener("change", () => {
		const value = document.getElementById('sortSelect').value;

		document.getElementById('shuffle').style.display =
			value === "random" ? 'inline-block' : 'none';

		sortList(listContainer, value);
	});

	function addListItem(name, total, max, min,frag,  [q, statFilter, maxFilter, minFilter]) {
		const listItem = document.createElement("li");
		const string=`
<stat title="Go to Full Leaderboard of '${name.replaceAll("_"," ").replaceAll("."," ")}'" onclick="if(event.target.closest('a')) return; window.open('stat/${encodeURIComponent(name)}.html','_blank');">
<strong class=stathead>${name}</strong>
<div class="total"><div>Total: ${total}</div></div>
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
		<div class=inline>
			${min.players.map(player => `<span class="player"><a class='profile_link' href='player/${player}.html' target="_blank"><img class='inline_face' src='faces/${player}.png'>${player}</a></span>`).join(", ")}
		</div> 
	</div> 
</div>
</stat>
`;
		listItem.innerHTML = string

		listItem._search = {
			stat: name.toLowerCase().replaceAll("_", " ").replaceAll(".", " "),
			max: max.players.map(p => p.toLowerCase().replaceAll("_", " ").replaceAll(".", " ")),
			min: min.players.map(p => p.toLowerCase().replaceAll("_", " ").replaceAll(".", " "))
		};

		listItem._total = total;
		if (q){
			if(!match(q, statFilter, maxFilter, minFilter,listItem)){
				listItem.classList.add("hidden");
			}
		}
		frag.appendChild(listItem);
		return listItem;
	}

	function updateURL(query) {
		const url = new URL(window.location);
		if (query) {
			url.searchParams.set("q", query);
		} else {
			url.searchParams.delete("q");
		}
		history.replaceState(null, "", url);
	}

	let debounceTimer;

	function runFilter() {
		const value = filterInput.value.toLowerCase().replaceAll("_", " ").replaceAll(".", " ");

		const matches = computeMatches(
			value,
			document.getElementById("filterStat").checked,
			document.getElementById("filterMax").checked,
			document.getElementById("filterMin").checked,
			listContainer
		);

		applyVisibility(matches);
		updateURL(value);
	}

	filterInput.addEventListener("input", () => {
		clearTimeout(debounceTimer);
		debounceTimer = setTimeout(runFilter, 100);
	});

	document.getElementById('filterMax').addEventListener("input", runFilter);
	document.getElementById('filterStat').addEventListener("input", runFilter);
	document.getElementById('filterMin').addEventListener("input", runFilter);

	async function loadJSONData() {
		const response = await fetch("leaderboard.json");
		return await response.json();
	}

	async function processJSON(data) {
		let counter = 0;
		
		let frag = document.createDocumentFragment();
		const params = new URLSearchParams(window.location.search);
		const q = params.get("q");
		if (q) {
			filterInput.value = q.toLowerCase().replaceAll("_", " ").replaceAll(".", " ");	
		}
		const statFilter=document.getElementById("filterStat").checked;
		const maxFilter=document.getElementById("filterMax").checked;
		const minFilter=document.getElementById("filterMin").checked;
		for (const entry of data) {

			counter++;
			if (counter % 100 === 0) {
				listContainer.appendChild(frag);
				if (typeof scheduler !== "undefined" && typeof scheduler.yield === "function") {
					await scheduler.yield.bind(scheduler);
				}else{
					await  new Promise(r => setTimeout(r, 0));
				}
				frag = document.createDocumentFragment();
			}

			if (entry.name === 'minecraft.crafted.air') continue;

			const item = addListItem(entry.name, entry.total, entry.max, entry.min, frag , [q, statFilter, maxFilter, minFilter]);

			searchIndex.statName[item._search.stat] = item;

			for (const raw of entry.max.players) {
				const name = raw.toLowerCase().replaceAll("_", " ").replaceAll(".", " ");
				let player = searchIndex.players[name];
				if (!player) {
					player = { max: [], min: [] };
					searchIndex.players[name] = player
				}
				player.max.push(item);
			}

			for (const raw of entry.min.players) {
				const name = raw.toLowerCase().replaceAll("_", " ").replaceAll(".", " ");
				let player = searchIndex.players[name];
				if (!player) {
					player = { max: [], min: [] };
					searchIndex.players[name] = player;
				}
				player.min.push(item);
			}
		}
		listContainer.appendChild(frag);
		// initial full visibility
		const all = new Set(listContainer.children);
		applyVisibility(all);
		// apply query from URL if present
		
		runFilter();
	}

	loadJSONData()
		.then(processJSON)
		.catch(err => console.error(err));
});

function topFunction() {
	document.body.scrollTop = 0;
	document.documentElement.scrollTop = 0;
}

