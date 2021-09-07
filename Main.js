const simbad = require("./modules/Simbad.js");
const fs = require("fs");
const path = require("path");

const infos = require("./infos.json");
const { info } = require("console");

var requester = new simbad.Simbad();

function sleep(ms) {
    return new Promise((resolve) => {
      setTimeout(resolve, ms);
    });
}   

// requester.GetObjectByID("HD 172167", (obj1) => {
//     requester.GetObjectByID("HD 187642", (obj2) => {
//         console.log("Obj1: " + obj1.ToString());
//         console.log("Obj2: " + obj2.ToString());
//         console.log(obj2.AngleTo(obj1).ToString());
//     });   
// });

const STAR_COUNT = infos["star-count"];

var finished = 0;
var sumString = [ ];

async function Main() 
{
    for (var i = infos.i; i <= STAR_COUNT; i++) {
        try {
            await new Promise((res, rej) => { 
                requester.GetObjectByID("HD " + i, (obj) => { 
                    try {
                        sumString.push(obj.ToCSV());
                    } catch {
                        console.log(`'${obj.id}' caused an error`)
                    }
                    if (++finished == STAR_COUNT) {
                        fs.writeFileSync(path.join(__dirname, "output.csv"), sumString.sort((a, b) => { 
                            if (a > b) return 1;
                            else if (a < b) return -1;
                            return 0;
                        }).join(""));
                        console.log("Wrote to file '" + path.join(__dirname, "output.csv") + "'");
                    }
                    // console.log(obj.id + " passed");
                    fs.writeFileSync(path.join(__dirname, "infos.json"), JSON.stringify({ i: Number(obj.id.replace("HD ", "")), "star-count": 5000 }));
                    res();
                });
            });
        } catch {
            console.log("HD " + i + " caused an error");
        }
    }
}

Main();

// requester.GetObjectByID("HD 12", (obj) => {
//     console.log(obj.ToString())
// });