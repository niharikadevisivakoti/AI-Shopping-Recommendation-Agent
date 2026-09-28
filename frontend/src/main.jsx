import React, { useEffect, useState } from 'react';
import { createRoot } from 'react-dom/client';
import './styles.css';

const API = 'http://127.0.0.1:8000/api';
const USD_TO_INR = 96;

function Grid({ items, onOpen }) {
  return (
    <div className="grid">
      {items.map((p) => (
        <article
          className="card"
          key={p.id}
          onClick={() => onOpen(p)}
        >
          <img src={p.image} alt={p.name} />

          <div className="body">
            <small>{p.category}</small>

            <h3>{p.name}</h3>

            <div>
              <b>
                ₹{Math.round(p.price * USD_TO_INR).toLocaleString('en-IN')}
              </b>

              <span>★ {p.rating}</span>
            </div>
          </div>
        </article>
      ))}
    </div>
  );
}

function App() {
  const [products, setProducts] = useState([]);
  const [cats, setCats] = useState([]);
  const [q, setQ] = useState('');
  const [cat, setCat] = useState('');
  const [selected, setSelected] = useState(null);
  const [recs, setRecs] = useState([]);
  const [loading, setLoading] = useState(true);

  // AI Agent chat state
  const [chatOpen, setChatOpen] = useState(false);
  const [chatInput, setChatInput] = useState('');
  const [chatMessages, setChatMessages] = useState([
    {
      role: 'assistant',
      text: 'Hi! I can help you find products. Try asking something like "I need running shoes under ₹3000".'
    }
  ]);
  const [chatLoading, setChatLoading] = useState(false);

  const load = async () => {
    try {
      setLoading(true);

      let u = new URL(API + '/products');

      if (q) {
        u.searchParams.set('q', q);
      }

      if (cat) {
        u.searchParams.set('category', cat);
      }

      const r = await fetch(u);
      const data = await r.json();

      setProducts(data.products || []);
    } catch (error) {
      console.error('Products loading error:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetch(API + '/categories')
      .then((r) => r.json())
      .then((x) => setCats(x.categories || []))
      .catch((error) =>
        console.error('Categories error:', error)
      );

    load();
  }, []);

  useEffect(() => {
    const t = setTimeout(load, 250);

    return () => clearTimeout(t);
  }, [q, cat]);

  const open = async (p) => {
    try {
      let ids = JSON.parse(
        localStorage.getItem('viewed') || '[]'
      ).filter((x) => x !== p.id);

      ids.unshift(p.id);
      ids = ids.slice(0, 5);

      localStorage.setItem(
        'viewed',
        JSON.stringify(ids)
      );

      const [
        similarResponse,
        recommendationsResponse
      ] = await Promise.all([
        fetch(`${API}/products/${p.id}/similar`),

        fetch(`${API}/recommendations`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            viewed_product_ids: ids,
            category: p.category,
            limit: 6
          })
        })
      ]);

      const similarData =
        await similarResponse.json();

      const recommendationsData =
        await recommendationsResponse.json();

      setSelected({
        ...p,
        similar: similarData.products || []
      });

      setRecs(
        recommendationsData.products || []
      );

    } catch (error) {
      console.error(
        'Product opening error:',
        error
      );

      setSelected({
        ...p,
        similar: []
      });
    }
  };

  // AI Agent function
  const sendChat = async () => {
    const message = chatInput.trim();

    if (!message || chatLoading) {
      return;
    }

    setChatMessages((prev) => [
      ...prev,
      {
        role: 'user',
        text: message
      }
    ]);

    setChatInput('');
    setChatLoading(true);

    try {
      const response = await fetch(
        `${API}/agent/chat`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            message
          })
        }
      );

      const data = await response.json();

      setChatMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          text: data.message
        }
      ]);

    } catch (error) {
      console.error('AI Agent error:', error);

      setChatMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          text: 'Sorry, I could not connect to the AI shopping assistant.'
        }
      ]);
    } finally {
      setChatLoading(false);
    }
  };

  const handleChatKeyDown = (e) => {
    if (e.key === 'Enter') {
      sendChat();
    }
  };

  return (
    <>
      <header>
        <div className="nav">
          <b>
            Recom<span>Lab</span>
          </b>

          <input
            placeholder="Search products..."
            value={q}
            onChange={(e) => setQ(e.target.value)}
          />
        </div>
      </header>

      <main>
        {selected ? (
          <>
            <button
              className="back"
              onClick={() => setSelected(null)}
            >
              ← Back
            </button>

            <section className="detail">
              <img
                src={selected.image}
                alt={selected.name}
              />

              <div>
                <p className="muted">
                  {selected.category}
                </p>

                <h1>{selected.name}</h1>

                <p>{selected.description}</p>

                <h2>
                  ₹
                  {Math.round(
                    selected.price * USD_TO_INR
                  ).toLocaleString('en-IN')}
                </h2>

                <p>
                  ★ {selected.rating} ·{' '}
                  {selected.reviews.toLocaleString()} reviews
                </p>
              </div>
            </section>

            <section>
              <h2>Similar products</h2>

              <Grid
                items={selected.similar}
                onOpen={open}
              />
            </section>
          </>
        ) : (
          <>
            <section className="hero">
              <p className="pill">
                AI-POWERED DISCOVERY
              </p>

              <h1>
                Find products you'll
                <br />
                <span>actually love.</span>
              </h1>

              <p>
                Browse a curated catalog and get
                personalized recommendations powered
                by content similarity and recent activity.
              </p>
            </section>

            <div className="cats">
              <button
                className={!cat ? 'active' : ''}
                onClick={() => setCat('')}
              >
                All
              </button>

              {cats.map((c) => (
                <button
                  className={cat === c ? 'active' : ''}
                  onClick={() => setCat(c)}
                  key={c}
                >
                  {c}
                </button>
              ))}
            </div>

            <section>
              <div className="sectionHead">
                <h2>
                  {q || cat
                    ? 'Matching products'
                    : 'Explore products'}
                </h2>

                <span>
                  {products.length} items
                </span>
              </div>

              {loading ? (
                <p>Loading...</p>
              ) : (
                <Grid
                  items={products}
                  onOpen={open}
                />
              )}
            </section>

            {recs.length > 0 && (
              <section>
                <div className="sectionHead">
                  <h2>Recommended for you</h2>

                  <span>
                    Based on recent views
                  </span>
                </div>

                <Grid
                  items={recs}
                  onOpen={open}
                />
              </section>
            )}
          </>
        )}
      </main>

      {/* AI SHOPPING ASSISTANT */}

      {chatOpen && (
        <div className="chatBox">
          <div className="chatHeader">
            <b>AI Shopping Assistant</b>

            <button
              onClick={() => setChatOpen(false)}
            >
              ×
            </button>
          </div>

          <div className="chatMessages">
            {chatMessages.map((msg, index) => (
              <div
                key={index}
                className={
                  msg.role === 'user'
                    ? 'chatMessage userMessage'
                    : 'chatMessage assistantMessage'
                }
              >
                {msg.text}
              </div>
            ))}

            {chatLoading && (
              <div className="chatMessage assistantMessage">
                Thinking...
              </div>
            )}
          </div>

          <div className="chatInputArea">
            <input
              value={chatInput}
              onChange={(e) =>
                setChatInput(e.target.value)
              }
              onKeyDown={handleChatKeyDown}
              placeholder="Ask for a product..."
              disabled={chatLoading}
            />

            <button
              onClick={sendChat}
              disabled={chatLoading}
            >
              Send
            </button>
          </div>
        </div>
      )}

      <button
        className="chatButton"
        onClick={() => setChatOpen(!chatOpen)}
      >
        {chatOpen ? '×' : 'AI'}
      </button>

      <footer>
        Product Recommendation System · React + FastAPI + TF-IDF + AI Agent
      </footer>
    </>
  );
}

createRoot(
  document.getElementById('root')
).render(<App />);