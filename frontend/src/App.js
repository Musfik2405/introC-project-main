import React, { useState } from 'react';
import axios from 'axios';
import { Shield, Lock, Zap, Key, RefreshCw, Terminal, Activity, Network } from 'lucide-react';

const API_BASE = "http://localhost:8000/api";

function App() {
  const [activeCard, setActiveCard] = useState(null);
  const [mode, setMode] = useState("encrypt");
  const [inputText, setInputText] = useState("");
  
  const [keys, setKeys] = useState({ 
    key: "", key1: "", key2: "", bits: 512,
    p: 97, a: 2, b: 3, gx: 0, gy: 10, priv_a: 9, priv_b: 14 
  });
  
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [rsaSession, setRsaSession] = useState({ keys: null, cipher: null });

  const handleExecute = async () => {
    setLoading(true);
    try {
      const endpoints = {
        substitution: "/classical/substitution", 
        transposition: "/classical/transposition",
        des: "/symmetric/des", 
        aes: "/symmetric/aes", 
        rsa: "/public_key/rsa/execute", 
        ecc: "/public_key/ecc/execute"
      };
      const response = await axios.post(`${API_BASE}${endpoints[activeCard]}`, {
        ...keys, text: inputText, mode: mode,
        rsa_keys: rsaSession.keys, rsa_cipher: rsaSession.cipher
      });
      
      if (activeCard === 'rsa' && mode === 'encrypt') {
        setRsaSession({...rsaSession, cipher: response.data.raw_blocks});
      }
      setResult(response.data);
    } catch (err) { alert("Execution Failed. Check backend connection."); }
    setLoading(false);
  };

  const renderConsoleOutput = (data) => {
    if (!data) return <div className="text-slate-700 italic">// Awaiting algorithm execution...</div>;

    // --- 1. SUBSTITUTION FORMATTER ---
    if (activeCard === 'substitution') {
      const isAttack = data.mode === "ATTACK" || mode === "attack";
      
      return (
        <div className="space-y-4 text-emerald-400">
          <p className="text-yellow-400 font-black border-b border-slate-800 pb-1 uppercase">{data.title || "--- Substitution Analysis ---"}</p>
          
          {isAttack ? (
             <div className="space-y-4">
                <div className="bg-emerald-900/20 border border-emerald-500/30 p-4 rounded-2xl shadow-inner">
                  <p className="text-emerald-400 text-[10px] font-black uppercase mb-1 tracking-widest underline">★ Rank #1 Best Possible Plaintext:</p>
                  <p className="text-white font-mono text-sm break-all leading-relaxed">{data.best_guess || "Analyzing..."}</p>
                </div>
                
                <div>
                  <p className="text-slate-500 text-[10px] uppercase font-black mb-2 tracking-widest">Other Ranked Candidates:</p>
                  <div className="space-y-2 max-h-48 overflow-y-auto custom-scrollbar pr-2">
                    {data.candidates && data.candidates.slice(1).map((cand, i) => (
                      <div key={i} className="bg-slate-950 p-3 rounded-xl border border-slate-900 text-[10px] shadow-sm">
                        <p className="text-slate-600 font-bold mb-1">Candidate #{i+2} | Score: {cand[0]}</p>
                        <p className="text-white font-mono break-all">{cand[2]}</p>
                      </div>
                    ))}
                  </div>
                </div>
             </div>
          ) : (
             <div>
               <p className="text-blue-400 text-[10px] font-black uppercase mb-1 tracking-widest">{(data.mode || mode).toUpperCase()} RESULT:</p>
               <p className="text-white text-lg font-bold break-all bg-slate-950 p-5 rounded-2xl border border-slate-800 shadow-inner">
                 {data.manual_result || "Result will appear here"}
               </p>
             </div>
          )}

          <div className="grid grid-cols-3 gap-2 border-t border-slate-800 pt-4">
            <div className="bg-slate-950 p-2 rounded-xl border border-slate-800 h-32 overflow-y-auto custom-scrollbar text-[8px] shadow-inner">
              <p className="text-blue-400 font-bold mb-2 underline tracking-wider">LETTERS</p>
              {data.letter_freq && data.letter_freq.map((f, i) => <div key={i} className="flex justify-between border-b border-slate-900 py-0.5"><span>{f[0]}</span><span className="text-slate-400">{f[2]}%</span></div>)}
            </div>
            <div className="bg-slate-950 p-2 rounded-xl border border-slate-800 h-32 overflow-y-auto custom-scrollbar text-[8px] shadow-inner">
              <p className="text-blue-400 font-bold mb-2 underline tracking-wider">BIGRAMS</p>
              {data.bigrams && data.bigrams.map((f, i) => <div key={i} className="flex justify-between border-b border-slate-900 py-0.5"><span>{f[0]}</span><span className="text-slate-400">{f[2]}%</span></div>)}
            </div>
            <div className="bg-slate-950 p-2 rounded-xl border border-slate-800 h-32 overflow-y-auto custom-scrollbar text-[8px] shadow-inner">
              <p className="text-blue-400 font-bold mb-2 underline tracking-wider">TRIGRAMS</p>
              {data.trigrams && data.trigrams.map((f, i) => <div key={i} className="flex justify-between border-b border-slate-900 py-0.5"><span>{f[0]}</span><span className="text-slate-400">{f[2]}%</span></div>)}
            </div>
          </div>
        </div>
      );
    }

    // --- 2. DOUBLE TRANSPOSITION FORMATTER ---
    if (activeCard === 'transposition' && data.result) {
        return (
          <div className="space-y-2 text-emerald-400">
            <p className="text-yellow-400 font-black border-b border-slate-800 pb-1 uppercase">{data.title}</p>
            <p>(E)ncrypt or (D)ecrypt: <span className="text-white">{data.mode}</span></p>
            <p>Key 1: <span className="text-white">{data.key1}</span> | Key 2: <span className="text-white">{data.key2}</span></p>
            <p>{data.round_label}: <span className="text-white font-bold">{data.round_text}</span></p>
            <p className="mt-2 text-blue-400 font-bold underline underline-offset-4">{data.final_label}: <span className="text-white">{data.result}</span></p>
          </div>
        );
    }

    // --- 3. AES & DES FORMATTER ---
    if ((activeCard === 'aes' || activeCard === 'des') && data.round_keys) {
      return (
        <div className="space-y-4 text-emerald-400">
          <p className="text-yellow-400 font-black border-b border-slate-800 pb-1 uppercase">{data.title}</p>
          <p>{data.key_label}: <span className="text-white font-bold">{data.key}</span></p>
          <div>
            <p className="text-slate-500 text-[10px] uppercase font-black tracking-widest mb-2 underline">Round Keys</p>
            <div className="text-[10px] bg-slate-950 p-4 rounded-xl border border-slate-800 font-mono leading-relaxed max-h-40 overflow-y-auto custom-scrollbar">
              {Object.entries(data.round_keys).map(([label, keyVal]) => (
                <div key={label}><span className="text-blue-400">{label}:</span> <span className="text-white">{keyVal}</span></div>
              ))}
            </div>
          </div>
          <div className="bg-slate-900/50 p-5 rounded-3xl border border-slate-800 space-y-2">
            <p>Output (Encryption) Ciphertext: <span className="text-white font-bold break-all">{data.encryption.ciphertext}</span></p>
            <p>Encryption Time: <span className="text-emerald-500">{data.encryption.time}</span></p>
            <div className="pt-2 mt-2 border-t border-slate-800">
              <p>Output (Decryption) Original: <span className="text-white font-bold">{data.decryption.original}</span></p>
              <p>Decryption Time: <span className="text-emerald-500">{data.decryption.time}</span></p>
            </div>
          </div>
        </div>
      );
    }

    // --- 4. RSA FORMATTER (Now includes HEX blocks) ---
    if (activeCard === 'rsa') {
      if (data.full_keys_object) {
        return (
          <div className="space-y-4 text-emerald-400">
             <p className="text-purple-400 font-black border-b border-slate-800 pb-1 uppercase">{data.title}</p>
             <p>Key Size: {data.bits} bits | Generation Time: {data.time}</p>
             <p className="text-blue-400 text-[10px] font-black uppercase mt-2 tracking-widest">Public Key (e, n):</p>
             <p className="text-[10px] break-all bg-slate-950 p-3 rounded-xl border border-slate-800">({data.full_keys_object.public_key[0]}, {data.full_keys_object.public_key[1]})</p>
             <p className="text-blue-400 text-[10px] font-black uppercase mt-2 tracking-widest">Private Key (d, n):</p>
             <p className="text-[10px] break-all bg-slate-950 p-3 rounded-xl border border-slate-800">({data.full_keys_object.private_key[0]}, {data.full_keys_object.private_key[1]})</p>
             <p className="text-yellow-400 text-[10px] mt-2 border-t border-slate-800 pt-2 font-bold uppercase tracking-widest">Factorization Attack Demo: <span className="text-white font-normal">{data.attack}</span></p>
          </div>
        );
      } else if (data.hex) {
        // ENCRYPTION RESULT: Shows both raw and hex blocks
        return (
          <div className="space-y-4 text-emerald-400">
             <p className="text-blue-400 font-black border-b border-slate-800 pb-1 uppercase">{data.title}</p>
             
             {/* Integer Blocks */}
             <p className="text-slate-500 text-[10px] uppercase font-black tracking-widest mt-2 underline">Ciphertext blocks (integer):</p>
             <div className="max-h-32 overflow-y-auto custom-scrollbar bg-slate-950 p-2 rounded-xl border border-slate-800">
                {data.raw_blocks.map((block, i) => <p key={`raw-${i}`} className="text-[10px] break-all">Block {i+1}: {block}</p>)}
             </div>

             {/* Hex Blocks */}
             <p className="text-slate-500 text-[10px] uppercase font-black tracking-widest mt-4 underline">Ciphertext blocks (hex):</p>
             <div className="max-h-32 overflow-y-auto custom-scrollbar bg-slate-950 p-2 rounded-xl border border-slate-800">
                {data.hex.map((block, i) => <p key={`hex-${i}`} className="text-[10px] break-all text-white font-bold">Block {i+1}: {block}</p>)}
             </div>

             <p className="mt-4 pt-2 border-t border-slate-800 text-yellow-400 font-bold uppercase text-[10px]">Encryption Time: {data.time}</p>
          </div>
        );
      } else if (data.result) {
        // DECRYPTION RESULT
        return (
          <div className="space-y-4 text-emerald-400">
             <p className="text-red-400 font-black border-b border-slate-800 pb-1 uppercase">{data.title}</p>
             <p className="text-slate-500 text-[10px] uppercase font-black tracking-widest mt-2 underline">Decrypted message:</p>
             <p className="text-white text-sm bg-slate-950 p-4 rounded-xl border border-slate-800 leading-relaxed">{data.result}</p>
             <p className="mt-4 pt-2 border-t border-slate-800 text-yellow-400 font-bold uppercase text-[10px]">Decryption Time: {data.time}</p>
          </div>
        );
      }
    }

    // --- 5. ECC FORMATTER ---
    if (activeCard === 'ecc' && data.exchange) {
      return (
        <div className="space-y-4 text-emerald-400">
          <p className="text-yellow-400 font-black border-b border-slate-800 pb-1 uppercase">{data.title}</p>
          <div>
            <p className="text-slate-500 text-[10px] uppercase font-black tracking-widest mb-2 underline">List of Ps (Points)</p>
            <div className="text-[10px] bg-slate-950 p-4 rounded-xl border border-slate-800 break-words max-h-40 overflow-y-auto custom-scrollbar leading-relaxed">
              {data.all_points_Ps.map((p, i) => <span key={i} className="mr-3 inline-block">{Array.isArray(p) ? `(${p[0]},${p[1]})` : p}</span>)}
            </div>
          </div>
          <div className="bg-slate-900/50 p-6 rounded-3xl border border-slate-800 space-y-4 shadow-inner">
            <p className="text-xs uppercase tracking-widest text-blue-400">Calculated Group Elements:</p>
            <p className="text-[11px]">• Output: Private Key (a): <span className="text-white font-bold">{data.exchange.user_a.private}</span></p>
            <p className="text-[11px]">• Output: Public Key (A): <span className="text-white font-bold">({data.exchange.user_a.public[0]}, {data.exchange.user_a.public[1]})</span></p>
            <div className="pt-3 border-t-2 border-dashed border-slate-700 flex justify-between items-center">
              <span className="text-yellow-400 font-black text-xs uppercase tracking-widest">Shared Key (Secret)</span>
              <span className="text-white font-mono bg-emerald-500/20 px-4 py-2 rounded-xl border border-emerald-500/40 font-bold">({data.exchange.shared_secret[0]}, {data.exchange.shared_secret[1]})</span>
            </div>
          </div>
        </div>
      );
    }
    
    return <pre className="whitespace-pre-wrap leading-relaxed opacity-50">{JSON.stringify(data, null, 2)}</pre>;
  };

  const cards = [
    { id: 'substitution', name: 'Substitution', icon: <Shield />, color: 'from-blue-500 to-cyan-500' },
    { id: 'transposition', name: 'Transposition', icon: <RefreshCw />, color: 'from-purple-500 to-indigo-500' },
    { id: 'des', name: 'DES', icon: <Lock />, color: 'from-orange-500 to-red-500' },
    { id: 'aes', name: 'AES', icon: <Zap />, color: 'from-yellow-400 to-orange-500' },
    { id: 'rsa', name: 'RSA', icon: <Key />, color: 'from-pink-500 to-rose-500' },
    { id: 'ecc', name: 'ECC', icon: <Network />, color: 'from-emerald-500 to-teal-500' },
  ];

  return (
    <div className="min-h-screen bg-[#020617] text-slate-200 p-8 font-sans selection:bg-blue-500/20">
      <header className="max-w-6xl mx-auto mb-12 flex justify-between items-end border-b border-slate-800 pb-8">
        <div>
          <h1 className="text-6xl font-black text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-emerald-500 tracking-tighter">CRYPTODECK</h1>
          <p className="text-slate-500 text-xs font-bold uppercase tracking-widest mt-2">Analysis Arena</p>
        </div>
        {activeCard && <button onClick={() => {setActiveCard(null); setResult(null); setRsaSession({keys:null, cipher:null}); setMode("encrypt");}} className="text-slate-400 hover:text-white text-xs border border-slate-800 px-5 py-2 rounded-full font-bold transition-all hover:bg-slate-900 shadow-lg">BACK TO DECK</button>}
      </header>
      
      <main className="max-w-6xl mx-auto">
        {!activeCard ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 animate-in fade-in duration-500">
            {cards.map(card => (
              <div key={card.id} onClick={() => {setActiveCard(card.id); setMode("encrypt");}} className="bg-slate-900 border border-slate-800 p-8 rounded-[2.5rem] cursor-pointer hover:border-emerald-500 shadow-xl transition-all hover:translate-y-[-5px]">
                <div className={`w-14 h-14 rounded-2xl bg-gradient-to-br ${card.color} flex items-center justify-center mb-6`}>{React.cloneElement(card.icon, { className: "text-white", size: 28 })}</div>
                <h3 className="text-2xl font-bold tracking-tight uppercase">{card.name}</h3>
              </div>
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-10">
            <section className="bg-slate-900 border border-slate-800 rounded-[3.5rem] p-10 shadow-2xl">
              <h2 className="text-3xl font-black mb-8 uppercase tracking-tighter flex items-center gap-3"><Activity className="text-blue-400"/> {activeCard} ARENA</h2>
              
              {activeCard === 'ecc' ? (
                <div className="space-y-6">
                   <div className="bg-slate-950 p-6 rounded-3xl border border-slate-800 shadow-inner">
                    <p className="text-[10px] font-black text-slate-500 uppercase mb-4 tracking-widest underline">Input: Domain Parameters (p, a, b, Gx, Gy)</p>
                    <div className="grid grid-cols-5 gap-2">{['p','a','b','gx','gy'].map(f => <input key={f} type="number" value={keys[f]} className="bg-slate-900 border border-slate-800 p-3 rounded-xl text-white font-bold text-center text-sm outline-none focus:ring-1 focus:ring-emerald-500" onChange={e=>setKeys({...keys, [f]: parseInt(e.target.value) || 0})}/>)}</div>
                   </div>
                   <div className="bg-slate-950 p-6 rounded-3xl border border-slate-800 shadow-inner">
                    <p className="text-[10px] font-black text-slate-500 uppercase mb-4 tracking-widest underline">Input: User Private Keys</p>
                    <div className="flex gap-4">
                      <input type="number" value={keys.priv_a} className="flex-1 bg-slate-900 border border-slate-800 p-4 rounded-xl text-white font-bold outline-none focus:ring-1 focus:ring-emerald-500" placeholder="Private Key A" onChange={e=>setKeys({...keys, priv_a: parseInt(e.target.value) || 0})}/>
                      <input type="number" value={keys.priv_b} className="flex-1 bg-slate-900 border border-slate-800 p-4 rounded-xl text-white font-bold outline-none focus:ring-1 focus:ring-emerald-500" placeholder="Private Key B" onChange={e=>setKeys({...keys, priv_b: parseInt(e.target.value) || 0})}/>
                    </div>
                   </div>
                </div>
              ) : (
                <>
                  {activeCard === 'substitution' && (
                    <div className="grid grid-cols-3 bg-slate-950 p-1.5 rounded-2xl mb-6 border border-slate-800 gap-1">
                      <button onClick={() => setMode("encrypt")} className={`py-3 rounded-xl font-black text-[10px] tracking-widest transition-all ${mode === "encrypt" ? "bg-blue-600 shadow-lg text-white" : "text-slate-600 hover:text-slate-400 hover:bg-slate-900"}`}>ENCRYPT</button>
                      <button onClick={() => setMode("decrypt")} className={`py-3 rounded-xl font-black text-[10px] tracking-widest transition-all ${mode === "decrypt" ? "bg-red-600 shadow-lg text-white" : "text-slate-600 hover:text-slate-400 hover:bg-slate-900"}`}>DECRYPT</button>
                      <button onClick={() => setMode("attack")} className={`py-3 rounded-xl font-black text-[10px] tracking-widest transition-all ${mode === "attack" ? "bg-emerald-600 shadow-lg text-white" : "text-slate-600 hover:text-slate-400 hover:bg-slate-900"}`}>ATTACK ANALYSIS</button>
                    </div>
                  )}

                  {activeCard === 'transposition' && (
                    <div className="grid grid-cols-2 bg-slate-950 p-1.5 rounded-2xl mb-6 border border-slate-800 gap-1">
                      <button onClick={() => setMode("encrypt")} className={`py-3 rounded-xl font-black text-[10px] tracking-widest transition-all ${mode === "encrypt" ? "bg-blue-600 shadow-lg text-white" : "text-slate-600 hover:text-slate-400 hover:bg-slate-900"}`}>ENCRYPT</button>
                      <button onClick={() => setMode("decrypt")} className={`py-3 rounded-xl font-black text-[10px] tracking-widest transition-all ${mode === "decrypt" ? "bg-red-600 shadow-lg text-white" : "text-slate-600 hover:text-slate-400 hover:bg-slate-900"}`}>DECRYPT</button>
                    </div>
                  )}
                  
                  {activeCard === 'rsa' && rsaSession.keys && (
                    <div className="grid grid-cols-2 bg-slate-950 p-1.5 rounded-2xl mb-6 border border-slate-800 gap-1">
                      <button onClick={() => setMode("encrypt")} className={`py-3 rounded-xl font-black text-[10px] tracking-widest transition-all ${mode === "encrypt" ? "bg-blue-600 shadow-lg text-white" : "text-slate-600 hover:text-slate-400 hover:bg-slate-900"}`}>ENCRYPT</button>
                      <button onClick={() => setMode("decrypt")} className={`py-3 rounded-xl font-black text-[10px] tracking-widest transition-all ${mode === "decrypt" ? "bg-red-600 shadow-lg text-white" : "text-slate-600 hover:text-slate-400 hover:bg-slate-900"}`}>DECRYPT</button>
                    </div>
                  )}
                  
                  <textarea className="w-full bg-slate-950 border border-slate-800 rounded-[2rem] p-6 mb-4 h-44 text-white focus:ring-2 focus:ring-blue-500 outline-none transition-all placeholder:text-slate-700" placeholder={mode === "attack" ? "Paste Ciphertext here to crack it using Pattern Search Analysis..." : "Enter message payload for encryption/decryption..."} value={inputText} onChange={e=>setInputText(e.target.value)}/>
                  
                  {activeCard === 'transposition' && (
                      <div className="flex gap-4 mb-4">
                          <input type="text" className="flex-1 bg-slate-950 border border-slate-800 p-4 rounded-xl text-white font-bold outline-none focus:ring-1 focus:ring-purple-500" placeholder="Key 1 (e.g. 4132)" onChange={e => setKeys({...keys, key1: e.target.value})}/>
                          <input type="text" className="flex-1 bg-slate-950 border border-slate-800 p-4 rounded-xl text-white font-bold outline-none focus:ring-1 focus:ring-purple-500" placeholder="Key 2 (e.g. 3142)" onChange={e => setKeys({...keys, key2: e.target.value})}/>
                      </div>
                  )}

                  {activeCard === 'substitution' && mode !== "attack" && (
                       <input type="text" className="w-full bg-slate-950 border border-slate-800 p-4 rounded-xl text-white font-bold mb-4 outline-none focus:ring-1 focus:ring-blue-500" placeholder="Enter 26-letter Substitution Key" onChange={e => setKeys({...keys, key: e.target.value})}/>
                  )}

                  {activeCard === 'rsa' && !rsaSession.keys && (
                    <div className="space-y-4 mb-4">
                      <p className="text-[10px] font-black text-slate-500 uppercase tracking-widest px-2 underline">RSA Modulus Parameter</p>
                      <select className="w-full bg-slate-950 border border-slate-800 p-4 rounded-xl text-white font-bold outline-none cursor-pointer focus:ring-1 focus:ring-purple-500" value={keys.bits} onChange={e => setKeys({...keys, bits: parseInt(e.target.value)})}>
                        <option value="512">512 BITS (Standard Complexity)</option>
                        <option value="1024">1024 BITS (High Security)</option>
                      </select>
                      <button onClick={async () => {
                        setLoading(true);
                        try {
                          const res = await axios.get(`${API_BASE}/public_key/rsa/setup?bits=${keys.bits}`);
                          setRsaSession({ keys: res.data.full_keys_object, cipher: null });
                          setResult(res.data);
                        } catch(e) { alert("RSA Setup Failed. Is backend running?"); }
                        setLoading(false);
                      }} className="w-full py-5 bg-purple-600 rounded-2xl font-black shadow-lg hover:bg-purple-500 transition-all tracking-widest uppercase text-xs">GENERATE RSA SESSION KEYS</button>
                    </div>
                  )}
                </>
              )}
              
              {(activeCard !== 'rsa' || rsaSession.keys) && (
                <button 
                  onClick={handleExecute} 
                  disabled={loading} 
                  className={`w-full py-6 rounded-2xl font-black text-white shadow-2xl mt-4 tracking-widest uppercase transition-all disabled:opacity-30 ${mode === "attack" ? "bg-emerald-600 hover:bg-emerald-500" : "bg-blue-600 hover:bg-blue-500"}`}
                >
                  {loading ? "PROCESSING BITS..." : mode === "attack" ? "RUN INTELLIGENT CRACK" : "EXECUTE SECURITY ANALYSIS"}
                </button>
              )}
            </section>
            
            <section className="bg-black border border-slate-800 rounded-[3.5rem] p-10 font-mono relative overflow-hidden shadow-2xl flex flex-col h-[650px]">
               <div className="mb-6 text-slate-600 font-bold border-b border-slate-800 pb-3 flex justify-between items-center uppercase text-xs tracking-tighter">
                  <span className="flex items-center gap-2"><Terminal size={16}/> System_Log_Console</span>
               </div>
               <div className="overflow-y-auto flex-1 custom-scrollbar pr-2">
                  {renderConsoleOutput(result)}
               </div>
            </section>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;