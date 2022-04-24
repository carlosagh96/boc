// Use with w3.css

//Define in a <script> tag
//The keys in the JSON contain other elements to be hidden
/*
const the_json='{"sect1":["thing1","thing2"],"sect2":["crap1","crap2","crap3"]}';
const the_data=JSON.parse(the_json);
const the_data_keys=Object.keys(the_data);
const the_data_keys_ln=the_data_keys.length;
*/
function funVisible(id)
{
	let dom_elem=document.getElementById(id)
	if ((dom_elem.className.indexOf("w3-show")>-1))
	{
		return true;
	}
	else
	{
		return false;
	}
}

function funGetPopuli(parent=null)
{
	if (parent===null)
	{
		let list=the_data_keys;
		return list;
	}
	else
	{
		let list=the_data[parent];
		return list;
	}
}

//For simple level accordions
async function funAccSimple(id,parent)
{
	let populi=funGetPopuli(parent);
	let idx_max=populi.length;
	let idx=0;
	let closed_at_least_one=false;
	console.log("(Simple Accordion)\nParent is "+parent+"\nID from arg "+id);

	//hide the others except the one from the args
	while (idx<idx_max)
	{
		var id_curr=populi[idx];
		console.log("\tIndex "+idx);
		console.log("\tCurrent ID "+id_curr);
		if (id_curr==id)
		{
			console.log("\t\tCannot close this one");
		}
		else
		{
			console.log("\t\tChecking if open");
			let vsb=funVisible(id_curr);
			if (vsb===true)
			{
				console.log("\t\t\tClosing");
				let dom_elem=document.getElementById(id_curr)
				dom_elem.className=dom_elem.className.replace("w3-show","w3-hide");
				if (closed_at_least_one==false)
				{
					closed_at_least_one=true;
				}
			}
		}
		idx++;
	}

	//small sleep time
	if (closed_at_least_one==true)
	{
		console.log("\tClosed at least one...");
		await new Promise(r => setTimeout(r,100));
	}
	else
	{
		console.log("\tNothing was open...");
	}

	//toggle open/close this one
	let dom_elem=document.getElementById(id);
	if (dom_elem.className.indexOf("w3-show")==-1)
	{
		console.log("\tOpened!");
		dom_elem.className=dom_elem.className.replace("w3-hide","w3-show");
		await new Promise(r => setTimeout(r,50));
		window.location="#"+id;
		//window.scrollBy(0,-72);
	}
	else
	{
		console.log("\nClosed!");
		dom_elem.className=dom_elem.className.replace("w3-show","w3-hide");
	}
}

//For group level accordions
async function funAccGroup(id)
{
	let populi=funGetPopuli();
	let idx=0;
	let closed_at_least_one=false;
	console.log("(Group Accordion)\nID from arg "+id);

	//close the other big ones
	console.log("\tClosing other Meta accordions");
	while (idx<the_data_keys_ln)
	{
		let id_curr=populi[idx];
		console.log("\tIndex "+idx);
		console.log("\tCurrent ID "+id_curr);
		if (id===id_curr)
		{
			console.log("\t\tSkipping ID from arg");
		}
		else
		{
			console.log("\t\tClosing this one and its children");
			let populi_curr=funGetPopuli(id_curr);
			let index_max=populi_curr.length;
			let index=0;
			let vsb=funVisible(id_curr)
			if (vsb===true)
			{
				console.log("\t\tIt's open, checking children");
				while (index<index_max)
				{
					id_child=populi_curr[index];
					console.log("\t\t\tIndex "+index);
					console.log("\t\t\tCurrent ID "+id_child);
					let vsb_child=funVisible(id_child);
					if (vsb_child===true)
					{
						console.log("\t\t\tHiding...");
						let dom_elem=document.getElementById(id_child);
						dom_elem.className=dom_elem.className.replace("w3-show","w3-hide");
					}
					index++;
				}
				let dom_elem=document.getElementById(id_curr);
				dom_elem.className=dom_elem.className.replace("w3-show","w3-hide");
				if (closed_at_least_one===false)
				{
					closed_at_least_one=true;
				}
			}
		}
		idx++;
	}

	//small sleep time
	if (closed_at_least_one==true)
	{
		console.log("\tClosed at least one...");
		await new Promise(r => setTimeout(r,100));
	}
	else
	{
		console.log("\tNothing was open...");
	}

	//toggle open/close this one
	let dom_elem=document.getElementById(id);
	if (dom_elem.className.indexOf("w3-show")==-1)
	{
		console.log("\tOpened!");
		dom_elem.className=dom_elem.className.replace("w3-hide","w3-show");
		await new Promise(r => setTimeout(r,50));
		window.location="#"+id;
		//window.scrollBy(0,-72);
	}
	else
	{
		console.log("\nClosed!");
		dom_elem.className=dom_elem.className.replace("w3-show","w3-hide");
	}
}
