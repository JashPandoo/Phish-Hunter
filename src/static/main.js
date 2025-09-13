let questions = [];
let currentIndex = 0;
const LEVEL_XP = 30;

async function fetchQuestions() {
  const res = await fetch("/api/questions");
  questions = await res.json();
  currentIndex = 0;
  renderQuestion();
  await fetchStatus();
}

async function fetchStatus(){
  const res = await fetch("/api/status");
  const st = await res.json();
  updateXPUI(st.xp, st.level);
  // document.getElementById("streak").innerText = st.streak;
  // renderBadges(st.badges);
}

function renderBadges(badges){
  
}

function renderQuestion(){
  const q = questions[currentIndex];
  if (!q) {
    document.getElementById("prompt").innerText = "No more questions! Great job.";
    document.getElementById("options").innerHTML = "";
    return;
  }
  document.getElementById("category").innerText = q.category.toUpperCase();
  document.getElementById("prompt").innerText = q.prompt;
  const opts = document.getElementById("options");
  opts.innerHTML = "";
  q.options.forEach((o,i) => {
    const div = document.createElement("div");
    div.className = "option";
    div.innerText = o;
    div.onclick = () => submitAnswer(q.id, i, div);
    opts.appendChild(div);
  });

  document.getElementById("feedback").classList.add("hidden");
  document.getElementById("question-card").classList.remove("hidden");
}

async function submitAnswer(qid, idx, el){
  // disable options
  document.querySelectorAll(".option").forEach(o => o.style.pointerEvents = "none");
  const res = await fetch("/api/answer", {
    method: "POST",
    headers: {"Content-Type":"application/json"},
    body: JSON.stringify({question_id: qid, selected_index: idx})
  });
  const data = await res.json();
  showFeedback(data, idx);
}

// function showFeedback(data, selectedIdx){
//   const fb = document.getElementById("feedback");
//   fb.classList.remove("hidden");
//   document.getElementById("question-card").classList.add("hidden");
//   const result = document.getElementById("result");
//   if (data.correct){
//     result.innerText = `Correct! +${data.xp_gained} XP`;
//     result.style.color = "#7af";
//     // confetti on level up (simple)
//     if (data.level > parseInt(document.getElementById("level").innerText.split(" ")[1])){
//       runConfetti();
//     }
//   } else {
//     result.innerText = `Not Quite — ${data.xp_gained} XP`;
//     result.style.color = "#f77";
//   }
//   document.getElementById("hint").innerText = data.hint || "";
//   updateXPUI(data.xp_total, data.level);
//   document.getElementById("streak").innerText = data.streak;
//   renderBadges(data.badges || []);
//   if (data.badge_unlocked){
//     // small popup
//     alert("Badge unlocked: " + data.badge_unlocked);
//   }
//   // next button moves to next
//   document.getElementById("next-btn").onclick = () => {
//     currentIndex++;
//     if (currentIndex >= questions.length) {
//       // reshuffle by fetching again
//       fetchQuestions();
//     } else {
//       renderQuestion();
//     }
//   }
// }

function updateXPUI(xp, level){
  document.getElementById("xp").innerText = xp;
  document.getElementById("level").innerText = "Level " + level;
  const pct = Math.min(100, (xp % LEVEL_XP) / LEVEL_XP * 100);
  document.getElementById("xp-fill").style.width = pct + "%";
  document.getElementById("xp-text").innerText = `${xp} XP (Level ${level})`;
}

// very simple confetti effect
function runConfetti(){
  for (let i=0;i<40;i++){
    const c = document.createElement('div');
    c.style.position='fixed';
    c.style.left=(50+Math.random()*40-20)+'%';
    c.style.top=(40+Math.random()*10)+'%';
    c.style.width = (6+Math.random()*8)+'px';
    c.style.height = (6+Math.random()*8)+'px';
    c.style.background = `hsl(${Math.random()*360} 80% 60%)`;
    c.style.opacity = '0.9';
    c.style.transform = 'rotate('+ (Math.random()*360) +'deg)';
    c.style.borderRadius='2px';
    c.style.zIndex=9999;
    document.body.appendChild(c);
    // animate
    c.animate([
      {transform: 'translateY(0) rotate(0)', opacity:1},
      {transform: `translateY(${200+Math.random()*300}px) rotate(${Math.random()*360}deg)`, opacity:0}
    ], {
      duration: 1200 + Math.random()*800,
      easing: 'cubic-bezier(.2,.6,.2,1)'
    });
    setTimeout(()=>c.remove(), 2000);
  }
}

function showFeedback(data, selectedIdx){
  const fb = document.getElementById("feedback");
  fb.classList.remove("hidden");
  document.getElementById("question-card").classList.add("hidden");
  const result = document.getElementById("result");
  if (data.correct){
    result.innerText = `Correct! +${data.xp_gained} XP`;
    result.style.color = "#7af";
  } else {
    result.innerText = `Not Quite — ${data.xp_gained} XP`;
    result.style.color = "#f77";
  }
  document.getElementById("hint").innerText = data.hint || "";
  updateXPUI(data.xp_total, data.level);
  document.getElementById("next-btn").onclick = () => {
    if (data.game_completed) {
      window.location.href = "/end";
      return;
    }
    if (data.level_completed) {
      runConfetti();
      setTimeout(fetchQuestions, 1200);
      return;
    } else {
      currentIndex++;
      if (currentIndex >= questions.length) {
        alert("You need more XP to pass this level. Try again!");
        fetchQuestions();
      } else {
        renderQuestion();
      }
    }
  }
}
window.onload = () => {
  fetchQuestions();
}