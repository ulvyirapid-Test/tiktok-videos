# AI Agent ដំបូងរបស់អ្នក (Make + Telegram + Google Sheets) — Script v1 (រង់ចាំការអនុម័ត)

Research (vidIQ, TikTok outliers, Mar–Nov 2026): @brycent_ "build a team of AI agents" 5.8M · @rachel.tyers AI bots for business 1.4M · @creators.hustle "I gave an AI agent a job" 672K · @viralex.aii Claude Code setup 1.1M.
Pattern: hook shows a real agent doing a job → simple parts → step-by-step build → result.

| # | On-screen | Narration (Khmer voice) |
|---|---|---|
| 1 Hook | Telegram chat: «ឡានណាត្រូវប្តូរប្រេងសប្តាហ៍នេះ?» → 🤖 «៣ គ្រឿង៖ …» · "AI Agent ធ្វើការ ២៤/៧" | (greeting) … ឧទាហរណ៍៖ សួរក្នុង Telegram ថា ឡានណាត្រូវប្តូរប្រេង — AI Agent បើក Google Sheet រកចម្លើយ ហើយឆ្លើយភ្លាម។ |
| 2 Chatbot vs Agent | Chatbot = ឆ្លើយពីអ្វីដែលវាដឹង · Agent = អានទិន្នន័យ · សម្រេចចិត្ត · ប្រើឧបករណ៍ | Chatbot ធម្មតា ឆ្លើយតែពីអ្វីវាដឹង។ AI Agent អាចចូលទៅមើលទិន្នន័យពិតរបស់អ្នក ហើយធ្វើការងារបាន។ |
| 3 ៤ ផ្នែក | 📩 Trigger · 🧠 AI Model · 📝 System prompt · 🛠️ Tools | Agent មាន ៤ ផ្នែក៖ អ្វីដាស់វា, ខួរក្បាល, សេចក្តីណែនាំការងារ, និងឧបករណ៍ដែលវាប្រើ។ |
| 4 ជំហាន ១ | Telegram → @BotFather → /newbot → Token 🔑 | បង្កើត Bot ក្នុង Telegram តាម BotFather ហើយចម្លង Token។ |
| 5 ជំហាន ២ | Make → Create scenario → Telegram Bot «Watch Updates» | ក្នុង Make បង្កើត Scenario ហើយដាក់ Telegram Watch Updates ជាអ្នកដាស់ Agent។ |
| 6 ជំហាន ៣ | AI Agent → ជ្រើស Model (OpenAI…) → System prompt: «អ្នកជាជំនួយការ Fleet · ឆ្លើយជាខ្មែរ · ប្រើតែទិន្នន័យក្នុង Sheet» | បន្ថែម AI Agent ជ្រើស Model ហើយសរសេរ System prompt ប្រាប់តួនាទី និងច្បាប់។ |
| 7 ជំហាន ៤ | Tool: Google Sheets «Search Rows» → តារាងឡាន | ឱ្យវាមានឧបករណ៍ Search Rows ដើម្បីរកទិន្នន័យក្នុង Google Sheet។ |
| 8 ជំហាន ៥ | Telegram «Send a Text Message» → Run once → សាកសួរ ✅ | បន្ថែមម៉ូឌុលផ្ញើសារត្រឡប់ ចុច Run once ហើយសាកសួរក្នុង Telegram។ |
| 9 ត្រូវដឹង | 💳 Make គិត Credits · 🧠 Agent មិនចាំការសន្ទនាមុន · 🧪 សាកក្នុង Testing & Training · 🔒 កុំឱ្យសិទ្ធិលុបទិន្នន័យ | ចំណុចត្រូវដឹង … |
| 10 CTA | «អ្នកចង់ឱ្យ AI Agent ធ្វើការងារអ្វីជំនួសអ្នក? 👇» | Follow · Comment |

Length target ≈ 2 min. Facts: help.make.com/create-your-first-ai-agent, make.com/en/how-to-guides/build-ai-agents (agents don't retain memory between runs).
