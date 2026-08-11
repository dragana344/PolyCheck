"""
Benchmark dataset generator.

Generates realistic sentence datasets for performance testing by
weighted-random sampling from template pools.  Each pool corresponds to
one error category so the resulting dataset has a controlled, reproducible
mix of correct sentences and sentences with specific kinds of errors.

Design constraints
------------------
- NO static files of thousands of sentences.
- All sentences are composed from a small number of hand-written templates.
- Results are reproducible when the same seed is used.
- Templates are real sentences, not Lorem Ipsum filler.

Supported languages: en (English), mk (Macedonian)

CLI usage
---------
    python benchmarks/dataset_generator.py --language en --size 1000
    python benchmarks/dataset_generator.py --language mk --size 500 --output data.txt
"""

from __future__ import annotations

import random
from typing import List, Tuple

# ─────────────────────────────────────────────────────────────────────────────
# English sentence pools
# ─────────────────────────────────────────────────────────────────────────────

_EN_CORRECT: List[str] = [
    "The quick brown fox jumps over the lazy dog.",
    "She bought fresh vegetables at the market today.",
    "He reads books every evening before going to bed.",
    "The weather today is warm and pleasant.",
    "Children are playing in the park near the lake.",
    "The scientist discovered a new species last year.",
    "They finished the project on time and within budget.",
    "The library opens at nine o'clock every morning.",
    "She learned to play the piano at an early age.",
    "The train arrived at the station thirty minutes late.",
    "He wrote a long letter to his friend overseas.",
    "The chef prepared a delicious meal for all the guests.",
    "She graduated from university with top grades.",
    "The meeting was scheduled for Tuesday afternoon.",
    "He repaired the car engine himself over the weekend.",
    "The birds migrated south for the winter season.",
    "She planted flowers in the garden every spring.",
    "The company launched a new product this quarter.",
    "He climbed the mountain with great determination.",
    "The team celebrated their victory with great joy.",
    "She studied hard for the final examination.",
    "The river flooded after the heavy rainfall last night.",
    "He donated a large sum of money to the local charity.",
    "The museum exhibit opened to the public today.",
    "She cooked dinner for her entire family every evening.",
    "The students submitted their reports on time.",
    "He repaired the fence around the backyard himself.",
    "The concert was attended by thousands of enthusiastic fans.",
    "She traveled to three different countries in one month.",
    "The journalist published an article about the recent event.",
    'She said "hello" and smiled warmly.',
    'He read "the rules are clear" out loud.',
    "She arrived early (as usual) and prepared everything.",
    "The result (as expected) was very positive.",
    "She ate an apple and an orange for breakfast.",
    "He carried an umbrella on a rainy day.",
    "She doesn't know the answer to the question.",
    "They can't come to the party tonight.",
    "She should have called before coming over.",
    "You're welcome to join us for dinner.",
    "There is a problem with the current plan.",
    "I don't have any money left in my wallet.",
    "She never said anything about the problem.",
    "However, the final result was very positive.",
    "Therefore, we decided to postpone the event.",
]

_EN_DOUBLE_SPACE: List[str] = [
    "The quick  brown fox jumps over the lazy dog.",
    "She bought  fresh vegetables at the market today.",
    "He reads  books every evening before going to bed.",
    "The weather  today is very warm and pleasant.",
    "Children are  playing in the park near the lake.",
    "The scientist  discovered a new species last year.",
    "They finished  the project on time and within budget.",
    "The library  opens at nine o'clock every morning.",
    "She learned  to play the piano at an early age.",
    "The train  arrived at the station thirty minutes late.",
]

_EN_REPEATED_WORD: List[str] = [
    "She went to to the store to buy groceries.",
    "The the dog barked loudly at the stranger.",
    "He is is very happy about the result today.",
    "They they finished all the work before noon.",
    "The cat sat on on the mat by the window.",
    "She bought apples and and oranges at the market.",
    "He walked walked slowly to the bus station.",
    "The bird bird sang beautifully in the tall tree.",
    "She is very very happy about the good news.",
    "He read the the entire book in one sitting.",
]

_EN_MISSING_PUNCT: List[str] = [
    "The cat sat on the mat by the window",
    "She is very happy about the final result",
    "He went to the store to buy fresh bread",
    "The dog barked loudly at the passing stranger",
    "She bought fresh vegetables at the local market",
    "He reads books every single evening before bed",
    "The weather today is warm and very pleasant",
    "Children are playing happily in the nearby park",
    "She learned how to play the piano as a child",
    "The train finally arrived at the station on time",
]

_EN_SPACE_BEFORE_PUNCT: List[str] = [
    "She bought apples ,oranges and fresh bananas.",
    "The answer is yes ,but we still need to check.",
    "He agreed with the plan ,and she was very happy.",
    "The meeting started late ,and it ended early.",
    "She arrived early ,prepared everything ,and waited.",
    "He said hello to everyone ,and then quickly left.",
    "They ordered pizza ,pasta and a fresh salad.",
    "The car suddenly stopped ,and the door opened.",
    "She smiled ,waved her hand and walked away.",
    "He finished the race first ,she finished second.",
]

_EN_TYPOS: List[str] = [
    "I thnk this is a really gret idea for us.",
    "She woud like to come and visit us tomrrow.",
    "He cam from a very smal town in the country.",
    "The wether was vrey nice and warm today.",
    "She stuied very hard for the important test.",
    "He wrte a long lettr to his old friend.",
    "The brid sang beautifully in the tall tre.",
    "She bught lots of fresh vegetbles at the market.",
    "He wokred all nght long to finish the project.",
    "The techer gave hm a very good grade for effort.",
]

_EN_NO_CAPITAL: List[str] = [
    "the dog barked loudly at the passing stranger.",
    "she went to the local market this morning.",
    "he is considered a very good and hardworking student.",
    "the weather outside is very nice and sunny today.",
    "she bought fresh apples and ripe oranges at the market.",
]

_EN_CONSECUTIVE_PUNCT: List[str] = [
    "What a great idea!!",
    "Really?? I can't believe it.",
    "She said goodbye.,and left the room.",
    "He finished the race.. finally.",
    "That is incredible!! Well done everyone.",
    "Are you sure?? This seems completely wrong.",
    "She smiled.,waved her hand and walked away.",
    "He won the award!! What an achievement.",
    "Is that true?? Please confirm right away.",
    "She typed the message.,and immediately sent it.",
]

_EN_UNBALANCED_QUOTES: List[str] = [
    'He said "hello and walked away quickly.',
    'She replied "I will be there very soon.',
    'The sign read "Do not enter the building.',
    'He whispered "please be quiet in the hall.',
    'She wrote "thank you in her personal diary.',
    'The teacher said "open your books to page ten.',
    'He announced "the meeting is now officially over.',
    'She asked "can you please help me with this.',
    'The note on the door said "call me tomorrow.',
    'He replied "I completely agree with your point.',
]

_EN_UNBALANCED_PARENS: List[str] = [
    "She explained the entire process (step by step.",
    "The result (as everyone expected was very good.",
    "He bought apples (and oranges at the market.",
    "The report (submitted on Monday was approved.",
    "She called her friend (who lives abroad.",
    "The meeting started late (as usual.",
    "He finished the project (ahead of the deadline.",
    "The dog sat quietly (waiting for its owner.",
    "She opened the letter (and read it carefully.",
    "The car stopped suddenly (blocking the entire road.",
]

_EN_ARTICLE_BEFORE_VOWEL: List[str] = [
    "She ate a apple for breakfast this morning.",
    "He saw a elephant at the zoo yesterday.",
    "It was a umbrella she had left behind.",
    "She found a old letter in the drawer.",
    "He adopted a orange cat last summer.",
    "She bought a unusual gift for her friend.",
    "He drove a old car to work every day.",
    "She wore a elegant dress to the party.",
    "He ate a entire pizza by himself tonight.",
    "She carried a empty box to the storage room.",
]

_EN_COMMON_CONFUSION: List[str] = [
    "You should of called before coming over.",
    "I would of gone if I had known earlier.",
    "She could of helped us with the problem.",
    "He must of forgotten about our appointment.",
    "Your welcome to join us for dinner tonight.",
    "Their is a serious problem with the plan.",
    "Their are many reasons to be optimistic.",
    "I should of studied harder for the exam.",
    "She would of won if she had tried harder.",
    "He could of done better with more effort.",
]

_EN_APOSTROPHE: List[str] = [
    "I dont know what to do about this problem.",
    "She doesnt care about the final result at all.",
    "He cant go to the party this weekend.",
    "Theyre coming over for dinner tonight.",
    "He wont help with the project at all.",
    "She isnt sure about the final answer.",
    "They arent ready for the big presentation.",
    "He wasnt there when we needed him most.",
    "She wouldnt agree to the new terms.",
    "I couldnt believe what he told me.",
]

_EN_DOUBLE_NEGATION: List[str] = [
    "I don't have no money left in my wallet.",
    "She never said nothing about the problem.",
    "I can't find nobody to help me today.",
    "He doesn't know nothing about the subject.",
    "She won't go nowhere without her friend.",
    "I can't do nothing right according to him.",
    "He never told nobody about the secret.",
    "She doesn't want no help from anyone here.",
    "I haven't seen nobody here all morning.",
    "He wouldn't give nobody a straight answer.",
]

_EN_INTRODUCTORY_COMMA: List[str] = [
    "However the final result was very disappointing.",
    "Therefore we decided to postpone the meeting.",
    "Furthermore the evidence clearly supports our claim.",
    "Moreover the team worked extra hours this week.",
    "Nevertheless she continued working on the project.",
    "Consequently the entire plan had to be revised.",
    "Additionally the report needs a second review.",
    "Finally the long awaited results were published.",
    "Meanwhile the other team finished their own work.",
    "Thus the conclusion is clear and well supported.",
]

# Pool definitions: (sentence list, sampling weight)
_EN_POOLS: List[Tuple[List[str], float]] = [
    (_EN_CORRECT,              0.25),
    (_EN_DOUBLE_SPACE,         0.07),
    (_EN_REPEATED_WORD,        0.07),
    (_EN_MISSING_PUNCT,        0.10),
    (_EN_SPACE_BEFORE_PUNCT,   0.07),
    (_EN_TYPOS,                0.08),
    (_EN_NO_CAPITAL,           0.06),
    (_EN_CONSECUTIVE_PUNCT,    0.04),
    (_EN_UNBALANCED_QUOTES,    0.04),
    (_EN_UNBALANCED_PARENS,    0.04),
    (_EN_ARTICLE_BEFORE_VOWEL, 0.04),
    (_EN_COMMON_CONFUSION,     0.04),
    (_EN_APOSTROPHE,           0.04),
    (_EN_DOUBLE_NEGATION,      0.03),
    (_EN_INTRODUCTORY_COMMA,   0.03),
]


# ─────────────────────────────────────────────────────────────────────────────
# Macedonian sentence pools
# ─────────────────────────────────────────────────────────────────────────────

_MK_CORRECT: List[str] = [
    "Лисицата брзо скокна преку мрзливото куче.",
    "Таа отиде на пазар да купи свеж зеленчук.",
    "Тој чита книги секоја вечер пред да заспие.",
    "Времето денес е многу убаво и пријатно.",
    "Децата играат во паркот крај езерото.",
    "Научникот откри нов вид на инсекти минатата година.",
    "Тие го завршија проектот навреме и во рамките на буџетот.",
    "Библиотеката се отвора во девет часот секое утро.",
    "Таа научи да свири пијано на многу рана возраст.",
    "Возот пристигна на станицата дваесет минути доцна.",
    "Тој напишал долго писмо до својот пријател во странство.",
    "Готвачот подготви вкусен оброк за сите гости.",
    "Таа дипломираше на универзитетот со одлични оценки.",
    "Состанокот беше закажан за вторник попладне.",
    "Тој сам ја поправи колата преку целиот викенд.",
    "Птиците се одселија на југ за зимскиот период.",
    "Таа засади цвеќиња во градината секоја пролет.",
    "Компанијата лансираше нов производ на пазарот овој квартал.",
    "Тој се искачи на планината со голема упорност и одлучност.",
    "Тимот ја прослави победата со многу голема радост.",
    'Тој рече „здраво" и брзо си замина.',
    'Таа одговори „ќе дојдам" и излезе.',
    "Таа пристигна рано (како обично) и подготви сè.",
    "Резултатот (како очекувано) беше многу добар.",
    "Тој учи, но не разбира секогаш.",
    "Таа сакаше да оди, ама немаше време.",
    "Мрк облак се наближи над градот.",
    "Крстот на планината се гледа одалеку.",
]

_MK_DOUBLE_SPACE: List[str] = [
    "Лисицата брзо  скокна преку мрзливото куче.",
    "Таа отиде  на пазар да купи свеж зеленчук.",
    "Тој чита  книги секоја вечер пред да заспие.",
    "Времето денес  е многу убаво и пријатно.",
    "Децата играат  во паркот крај езерото.",
    "Научникот  откри нов вид на инсекти.",
    "Тие го  завршија проектот навреме.",
    "Библиотеката  се отвора рано секое утро.",
    "Таа научи  да свири пијано.",
    "Возот пристигна  на станицата многу доцна.",
]

_MK_REPEATED_WORD: List[str] = [
    "Таа таа отиде на пазарот денес.",
    "Тој тој чита книги секоја вечер.",
    "Времето денес е е многу убаво.",
    "Децата играат во во паркот крај езерото.",
    "Лисицата брзо скокна скокна преку куче.",
    "Научникот откри откри нов вид на инсекти.",
    "Тие го завршија завршија проектот навреме.",
    "Библиотеката се се отвора рано секое утро.",
    "Таа научи да да свири пијано.",
    "Возот пристигна пристигна многу доцна.",
]

_MK_MISSING_PUNCT: List[str] = [
    "Лисицата брзо скокна преку мрзливото куче",
    "Таа отиде на пазар да купи свеж зеленчук",
    "Тој чита книги секоја вечер пред да заспие",
    "Времето денес е многу убаво и пријатно",
    "Децата играат во паркот крај езерото",
    "Научникот откри нов вид на инсекти",
    "Тие го завршија проектот навреме",
    "Библиотеката се отвора рано секое утро",
    "Таа научи да свири пијано на рана возраст",
    "Возот пристигна многу доцна на станицата",
]

_MK_SPACE_BEFORE_PUNCT: List[str] = [
    "Таа купи јаболки ,портокали и свежи банани.",
    "Одговорот е да ,но сè уште треба да провериме.",
    "Тој се согласи со планот ,а таа беше многу среќна.",
    "Состанокот почна доцна ,а заврши многу рано.",
    "Таа пристигна рано ,подготви сè ,и почна да чека.",
    "Тој рече здраво на сите ,и веднаш си замина.",
    "Тие нарачаа пица ,паста и свежа зелена салата.",
    "Колата нагло запре ,и вратата се отвори.",
    "Таа насмевна ,климна со главата и тивко си замина.",
    "Тој заврши прв на трката ,а таа заврши втора.",
]

_MK_MIXED_SCRIPT: List[str] = [
    "Таа отиде на pazar да купи свеж зеленчук денес.",
    "Тој е mnogu добар и вреден student во класот.",
    "Времето denes е многу убаво и пријатно надвор.",
    "Децата играат vo паркот крај езерото секој ден.",
    "Лисицата brgu скокна преку мрзливото куче.",
    "Научникот otkrija нов вид на инсекти минатата година.",
    "Тие go завршија целиот проект навреме.",
    "Библиотеката se otвора рано секое утро.",
    "Таа nauci да свири пијано на рана возраст.",
    "Возот pristigna многу доцна на главната станица.",
]

_MK_NO_CAPITAL: List[str] = [
    "лисицата брзо скокна преку мрзливото куче.",
    "таа отиде на пазар да купи свеж зеленчук.",
    "тој чита книги секоја вечер пред да заспие.",
    "времето денес е многу убаво и пријатно.",
    "децата играат во паркот крај езерото.",
]

_MK_CONSECUTIVE_PUNCT: List[str] = [
    "Колку убаво!!",
    "Навистина?? Не можам да верувам.",
    "Таа рече збогум.,и веднаш си замина.",
    "Тој ја заврши трката.. конечно.",
    "Тоа е неверојатно!! Браво на сите.",
    "Дали си сигурен?? Ова изгледа погрешно.",
    "Таа се насмевна.,климна со главата и замина.",
    "Тој ја доби наградата!! Каков голем успех.",
    "Дали е тоа точно?? Потврди ве молам.",
    "Таа ја напиша пораката.,и веднаш ја испрати.",
]

_MK_UNBALANCED_QUOTES: List[str] = [
    'Тој рече "здраво и брзо си замина.',
    'Таа одговори "ќе бидам таму наскоро.',
    'Знакот пишуваше "не влегувај во просторијата.',
    'Тој прошепоти "ве молам бидете тивки.',
    'Таа напиша "благодарам во личниот дневник.',
    'Наставникот рече "отворете ги книгите.',
    'Тој објави "состанокот е официјално завршен.',
    'Таа праша "можеш ли да ми помогнеш со ова.',
    'Белешката пишуваше "јави ми се утре.',
    'Тој одговори "целосно се согласувам со тебе.',
]

_MK_UNBALANCED_PARENS: List[str] = [
    "Таа го објасни процесот (чекор по чекор.",
    "Резултатот (како што се очекуваше беше добар.",
    "Тој купи јаболки (и портокали на пазарот.",
    "Извештајот (поднесен в понеделник беше одобрен.",
    "Таа го повика пријателот (кој живее во странство.",
    "Состанокот почна доцна (како обично.",
    "Тој го заврши проектот (пред утврдениот рок.",
    "Кучето седеше тивко (чекајќи го сопственикот.",
    "Таа го отвори писмото (и внимателно го прочита.",
    "Колата нагло запре (блокирајќи го целиот пат.",
]

# Sentences with vowel-free Cyrillic tokens — almost certainly garbled typos.
_MK_CYRILLIC_NO_VOWEL: List[str] = [
    "Тоа е збрв текст напишан набрзина.",
    "Тој видел чдн нешто непознато во дворот.",
    "Таа прочита блт порака доцна вечерта.",
    "Тој напишал нчт нејасно на таблата.",
    "Таа пронашла стрн предмет во фиоката.",
    "Тој слушнал гдн звук доаѓа од соседната соба.",
    "Таа видела збрн знак на патот.",
    "Тој напишал мнг зборови без смисла.",
    "Таа прочитала крн порака во писмото.",
    "Тој оставил врш белешка на масата.",
]

# Sentences with Latin homoglyph characters embedded in Cyrillic text.
# The capitalised/ASCII letters below are intentionally Latin Unicode codepoints
# that are visually identical to their Cyrillic counterparts.
_MK_HOMOGLYPH: List[str] = [
    "Тоa е многу точно и јасно.",           # Latin 'a' (U+0061)
    "Тaa купи свеж леб денес наутро.",       # Latin 'a','a'
    "Oн отиде дома многу рано.",             # Latin 'O' (U+004F)
    "Cе работи добро и уредно тука.",        # Latin 'C' (U+0043)
    "Tаа е многу добра и вредна.",           # Latin 'T' (U+0054)
    "Таa e среќна и задоволна денес.",       # Latin 'a', 'e'
    "Kој е тој непознат човек таму?",        # Latin 'K' (U+004B)
    "Mногу убаво и пријатно надвор денес.",  # Latin 'M' (U+004D)
    "Pаботата е целосно завршена навреме.",  # Latin 'P' (U+0050)
    "Eдно многу убаво утро во градот.",      # Latin 'E' (U+0045)
]

_MK_COMMA_CONJUNCTION: List[str] = [
    "Тој учеше напорно но го положжи испитот.",
    "Таа беше уморна ама продолжи да работи.",
    "Тие не сакаа тоа туку нешто сосема друго.",
    "Времето беше убаво но ветрот беше силен.",
    "Тој дојде рано но веднаш си замина.",
    "Таа пееше убаво ама никој не слушаше.",
    "Тие не го земаа паричникот туку книгата.",
    "Тој беше гладен но немаше храна.",
    "Таа сакаше да оди ама немаше превоз.",
    "Тие не го завршија проектот туку само го започнаа.",
]

_MK_SPELL: List[str] = [
    "Денес врмето е многу убаво.",
    "Таа купи зеленчуг на пазарот денес.",
    "Книгта беше многу интересна за читање.",
    "Наставнкот го објасни правилото на час.",
    "Птицте пеат рано наутро во градинката.",
    "Малото дте се смееше гласно во паркот.",
    "Тој го посети убаото место во градот.",
    "Таа ги читаше весницте секое утро.",
    "Тие заминаа кон планниата за викенд.",
    "Момчто беше многу висок и силен.",
]

# Pool definitions: (sentence list, sampling weight)
_MK_POOLS: List[Tuple[List[str], float]] = [
    (_MK_CORRECT,              0.18),
    (_MK_DOUBLE_SPACE,         0.07),
    (_MK_REPEATED_WORD,        0.07),
    (_MK_MISSING_PUNCT,        0.08),
    (_MK_SPACE_BEFORE_PUNCT,   0.07),
    (_MK_MIXED_SCRIPT,         0.08),
    (_MK_NO_CAPITAL,           0.07),
    (_MK_CONSECUTIVE_PUNCT,    0.04),
    (_MK_UNBALANCED_QUOTES,    0.04),
    (_MK_UNBALANCED_PARENS,    0.04),
    (_MK_CYRILLIC_NO_VOWEL,    0.06),
    (_MK_HOMOGLYPH,            0.08),
    (_MK_COMMA_CONJUNCTION,    0.06),
    (_MK_SPELL,                0.06),
]

# ─────────────────────────────────────────────────────────────────────────────
# Turkish sentence pools
# ─────────────────────────────────────────────────────────────────────────────

_TR_CORRECT: List[str] = [
    "Bugün hava çok güzel ve sıcak.",
    "Ankara'da yaşayan arkadaşım bugün İstanbul'a gidecek.",
    "Mehmet'in kitabı masanın üzerinde kalmış.",
    "TBMM'ye sunulan tasarı bugün onaylandı.",
    "Atatürk'ün ilkeleri yolumuzu aydınlatıyor.",
    "İzmir'deki fuar yarın sona eriyor.",
    "Ayşe'nin çantası bugün parkta unutulmuş.",
    "Sınava girdin mi ve sonuçları aldın mı?",
    "Kitabı masaya bıraktım ve hemen odama geçtim.",
    "Bugün gökyüzü çok parlak ve açık görünüyor.",
    "Kardeşim parka gitmek için çok hevesli.",
    "Bilgisayarın ekranı dün akşam bozuldu.",
    "Yarın akşam sinemaya birlikte gidelim mi?",
    "Yaptığım ödevi öğretmene teslim ettim.",
    "İstanbul'un trafiği bitmiyor, herkes şikayetçi.",
    "Türkiye'nin başkenti Ankara'dır ve burası çok güzeldir.",
    "TDK'nın sitesine girdin mi ve kurallara baktın mı?",
    "Hazır mısın ve her şey tamam mı?",
    "Birçok insan toplantıya geldi.",
    "Her şey yolunda görünüyor.",
    "Dün akşamki konsere gitmeyi planlıyorduk.",
    "Konferans salonu katılımcılar için genişti.",
    "Yemekten sonra biraz dinlenmek için kahve içelim.",
    "Hukuku herkesin bilmesi gerekir.",
    "Doğum gününde ona güzel bir hediye aldım.",
    "Bahçedeki çiçekleri sulamayı unutma.",
    "Bugün mü geliyorsun, yoksa yarın mı?",
    "Parkta da çocuklar oynuyor, ne kadar mutlular.",
    "Türkiye'de yaşamak güzel, çünkü herkes birbirini anlıyor.",
    "Ders çalışmayı çok seviyorum ve her gün pratik yapıyorum.",
    'O "hayır" dedi ve hemen ayrıldı.',
    'Öğretmen "çok güzel" dedi ve güldü.',
    "Toplantı erken bitti (herkes memnundu).",
    "Sonuç (beklendiği gibi) çok iyiydi.",
    "2024'te önemli kararlar alındı.",
    "Saat 10'da buluşalım.",
]

_TR_APOSTROPHE: List[str] = [
    "TBMMde yeni bir yasa kabul edildi.",
    "TDKnin sözlüğünü sık kullanıyorum.",
    "TRTye yeni bir program eklendi.",
    "YÖKten açıklama yapıldı.",
    "SGKya başvurumu yaptım.",
    "TÜBİTAKta yeni projeler destekleniyor.",
    "ABDde eğitim görmek istiyorum.",
    "ABye üyelik süreci devam ediyor.",
    "THYnin yeni seferleri başladı.",
    "TÜİKten enflasyon verileri açıklandı.",
]

_TR_QUESTION_PARTICLE: List[str] = [
    "Geldinmi?",
    "Tamammı?",
    "Beni gördünmü?",
    "Hazırmısın?",
    "Mutlumusun?",
    "Gelecekmisin?",
    "Yaptınmı?",
    "Okudunmu?",
    "Duydunmu?",
    "Biliyormusun?",
]

_TR_NUMBER_SUFFIX: List[str] = [
    "Toplantı 2024te yapılacak.",
    "15inci sırada oturuyorum.",
    "Yarış 3üncü turda sona erdi.",
    "5e kadar bekle.",
    "Saat 10da buluşalım.",
    "100den fazla kişi geldi.",
    "7ye otobüs kalkacak.",
    "12yi geçmeden dön.",
    "29ekimde tören yapılacak.",
    "8inci katta çalışıyorum.",
]

_TR_BIRCOK: List[str] = [
    "Bir çok insan geldi.",
    "Bir çok öğrenci sınava girdi.",
    "Bir çok kitap okudum.",
    "Bir çok kişi katıldı.",
    "Bir çok ev satıldı.",
    "Bir çok fikir ortaya çıktı.",
    "Bir çok ülke katıldı.",
    "Bir çok çocuk oynuyordu.",
    "Bir çok soru çözdüm.",
    "Bir çok örnek bulduk.",
]

_TR_HER_SEY: List[str] = [
    "Herşey yolunda.",
    "Herşey çok güzel olacak.",
    "Herşey hazır mı?",
    "Herşey bitti.",
    "Herşey istediğin gibi oldu.",
    "Herşey zamanla düzelir.",
    "Herşey kontrol altında.",
    "Herşey masanın üzerinde.",
    "Herşey doğru görünüyordu.",
    "Herşey senin için.",
]

_TR_DOUBLE_SPACE: List[str] = [
    "Bugün  hava çok güzel.",
    "Sınav  zamanı  yaklaşıyor.",
    "Kitap  okumak  çok  faydalıdır.",
    "Yarın  pikniğe gidiyoruz.",
    "Bu araba  çok hızlı.",
    "Bilgisayar  bozuldu  galiba.",
    "Hava bugün  çok sıcak.",
    "Ders  çalışmayı  çok seviyorum.",
    "İstanbul'da  trafik  çok  yoğun.",
    "Arkadaşım  bugün  beni aradı.",
]

_TR_UNBALANCED_PARENS: List[str] = [
    "Yarınki toplantıya (Ahmet de katılacak.",
    "Proje ödevini teslim etmek için (son gün yarın.",
    "Yemekten sonra bir kahve içelim (yorgunluğumuz geçsin.",
    "Konferans salonu (herkese yetecek kadar büyük değil.",
    "Bu raporu hazırlarken verileri (dikkatli inceledik.",
    "Okulun bahçesindeki ağaçlar (çok büyümüş.",
    "Bugün hava güzel (dışarı çıkalım mı?",
    "Kitabı okumayı bitirince (çok etkilendim.",
    "Toplantı erken bitti (herkes memnundu.",
    "Arkadaşım geldi (çok sevindim.",
]

_TR_MISSING_PUNCT: List[str] = [
    "Bugün hava çok güzel ve sıcak",
    "Ankara'da yaşayan arkadaşım İstanbul'a gidecek",
    "Mehmet'in kitabı masanın üzerinde kalmış",
    "Sınava girdin mi ve sonuçları aldın mı",
    "Kardeşim parka gitmek için çok hevesli",
    "Bilgisayarın ekranı dün akşam bozuldu",
    "Yaptığım ödevi öğretmene teslim ettim",
    "Türkiye'nin başkenti Ankara'dır",
    "Dün akşamki konsere gitmeyi planlıyorduk",
    "Hukuku herkesin bilmesi gerekir",
]

_TR_NO_CAPITAL: List[str] = [
    "bugün hava çok güzel ve sıcak.",
    "ankara'da yaşayan arkadaşım İstanbul'a gidecek.",
    "kitabı masaya bıraktım ve hemen odama geçtim.",
    "yarın akşam sinemaya birlikte gidelim mi?",
    "dün akşamki konsere gitmeyi planlıyorduk.",
]

_TR_SPACE_BEFORE_PUNCT: List[str] = [
    "Bugün hava çok güzel ,değil mi?",
    "Kitabı okudum ,çok beğendim.",
    "Mehmet geldi ,ama erken ayrıldı.",
    "Toplantı başladı ,herkes hazırdı.",
    "Hava soğuk ,ama güneş parlıyor.",
    "Sınav zor değildi ,ama dikkat gerektirdi.",
    "Arkadaşım aradı ,yarın buluşacağız.",
    "Kahve içtim ,biraz dinlendim.",
    "Ders çalıştım ,ama yoruldum.",
    "Bahçeye çıktım ,hava çok güzeldi.",
]

_TR_CONSECUTIVE_PUNCT: List[str] = [
    "Ne güzel bir gün!!",
    "Gerçekten mi?? İnanamıyorum.",
    "Toplantı bitti.,herkes dağıldı.",
    "Harika!! Çok başarılı oldun.",
    "Emin misin?? Bu çok önemli.",
    "Ders bitti.. nihayet.",
    "Bravo!! Çok iyi yaptın.",
    "Doğru mu?? Lütfen onayla.",
    "Kitabı okudum.,çok etkilendim.",
    "Kazandık!! Ne harika bir zafer.",
]

_TR_UNBALANCED_QUOTES: List[str] = [
    'O "hayır dedi ve hemen ayrıldı.',
    'Öğretmen "çok güzel dedi ve devam etti.',
    'Kitapta "başarı çalışmayla gelir yazıyordu.',
    'Arkadaşım "yarın geleceğim dedi.',
    'Müdür "toplantı iptal edildi diye duyurdu.',
    'Anne "yemeğe gel diye seslendi.',
    'Haber "deprem oldu diye başlıyordu.',
    'O "bilmiyorum dedi ve sustdu.',
    'Raporda "sonuçlar olumlu yazıyordu.',
    'Öğrenci "anlamadım dedi sessizce.',
]

_TR_SPELL: List[str] = [
    "Bugün hava çok güzal ve sıcak.",
    "Masanın üzerindeki kitep kayboldu.",
    "Her zamin erken kalkmaya çalışırım.",
    "Bu insam çok yardımsever biri.",
    "Çocuklar okull koşarak gitti.",
    "Sınav sonuçları yarın açıklanacek.",
    "Arkadajım bugün erken geldi.",
    "Yemek çok lezzetliydi, hepimiz memnun oltek.",
    "Öğretmen dersi çok iyi anlattı, herkes anlodı.",
    "Bugün hava sıcak olduğu için dışarı çıkmak istiyoruz.",
]

# Pool definitions: (sentence list, sampling weight)
_TR_POOLS: List[Tuple[List[str], float]] = [
    (_TR_CORRECT,              0.18),
    (_TR_APOSTROPHE,           0.08),
    (_TR_QUESTION_PARTICLE,    0.08),
    (_TR_NUMBER_SUFFIX,        0.09),
    (_TR_BIRCOK,               0.07),
    (_TR_HER_SEY,              0.07),
    (_TR_DOUBLE_SPACE,         0.07),
    (_TR_UNBALANCED_PARENS,    0.06),
    (_TR_MISSING_PUNCT,        0.06),
    (_TR_NO_CAPITAL,           0.04),
    (_TR_SPACE_BEFORE_PUNCT,   0.04),
    (_TR_CONSECUTIVE_PUNCT,    0.04),
    (_TR_UNBALANCED_QUOTES,    0.06),
    (_TR_SPELL,                0.06),
]

_LANGUAGE_POOLS = {"en": _EN_POOLS, "mk": _MK_POOLS, "tr": _TR_POOLS}

# Standard benchmark sizes used by run_benchmarks.py
BENCHMARK_SIZES: List[int] = [400000]


# ─────────────────────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────────────────────

def generate(language: str, n: int, seed: int = 42) -> List[str]:
    """
    Generate *n* sentences for *language* by weighted random sampling.

    The result is reproducible for the same (language, n, seed) triple.
    Sentences are drawn with replacement, so the same template may appear
    multiple times in large datasets — this is intentional for load testing.

    Args:
        language: ISO 639-1 code.  Supported: "en", "mk".
        n:        Number of sentences to generate.
        seed:     Random seed for reproducibility.  Default: 42.

    Returns:
        List of *n* sentence strings.

    Raises:
        ValueError: if *language* is not supported.
    """
    if language not in _LANGUAGE_POOLS:
        available = ", ".join(sorted(_LANGUAGE_POOLS))
        raise ValueError(
            f"No sentence pool for language '{language}'. Available: {available}"
        )

    rng = random.Random(seed)
    pools_and_weights = _LANGUAGE_POOLS[language]
    pools   = [p for p, _ in pools_and_weights]
    weights = [w for _, w in pools_and_weights]

    sentences: List[str] = []
    for _ in range(n):
        pool = rng.choices(pools, weights=weights, k=1)[0]
        sentences.append(rng.choice(pool))

    return sentences


# ─────────────────────────────────────────────────────────────────────────────
# CLI entry point
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse
    import sys
    from pathlib import Path

    ap = argparse.ArgumentParser(
        description="Generate a benchmark sentence dataset.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python benchmarks/dataset_generator.py --language en --size 1000
  python benchmarks/dataset_generator.py --language mk --size 500 --output mk_500.txt
""",
    )
    ap.add_argument("--language", choices=list(_LANGUAGE_POOLS), required=True)
    ap.add_argument("--size", type=int, required=True)
    ap.add_argument("--output", default=None, metavar="FILE",
                    help="Write to FILE instead of stdout.")
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    sentences = generate(args.language, args.size, args.seed)
    text = "\n".join(sentences)

    if args.output:
        Path(args.output).write_text(text + "\n", encoding="utf-8")
        print(f"Wrote {len(sentences)} sentences to {args.output}")
    else:
        sys.stdout.write(text + "\n")
