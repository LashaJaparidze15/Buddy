import { useState, useEffect } from 'react';
import { getNews, getNewsCategories } from '../services/api';
import { ExternalLink } from 'lucide-react';

export default function News() {
  const [articles, setArticles] = useState([]);
  const [categories, setCategories] = useState([]);
  const [activeCategory, setActiveCategory] = useState('general');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getNewsCategories().then((res) => setCategories(res.data.categories));
  }, []);

  useEffect(() => {
    const fetchNews = async () => {
      setLoading(true);
      try {
        const response = await getNews(activeCategory);
        setArticles(response.data);
      } catch (err) {
        console.error('Failed to fetch news');
      } finally {
        setLoading(false);
      }
    };
    fetchNews();
  }, [activeCategory]);

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-800">News</h1>

      {/* Category Tabs */}
      <div className="flex flex-wrap gap-2">
        {categories.map((cat) => (
          <button
            key={cat}
            onClick={() => setActiveCategory(cat)}
            className={`px-4 py-2 rounded-lg capitalize transition-colors ${
              activeCategory === cat
                ? 'bg-cyan-600 text-white'
                : 'bg-white text-gray-600 hover:bg-gray-100'
            }`}
          >
            {cat}
          </button>
        ))}
      </div>

      {/* Articles */}
      {loading ? (
        <div className="text-center py-12 text-gray-500">Loading news...</div>
      ) : articles.length === 0 ? (
        <div className="bg-yellow-50 border border-yellow-200 p-6 rounded-xl">
          <p className="text-yellow-700">No news available. Check your API key.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {articles.map((article, i) => (
            <article key={i} className="bg-white rounded-xl shadow-sm overflow-hidden hover:shadow-md transition-shadow">
              <div className="p-5">
                <p className="text-sm text-cyan-600 font-medium mb-2">{article.source}</p>
                <h3 className="font-semibold text-gray-800 mb-2 line-clamp-2">
                  {article.title}
                </h3>
                <p className="text-gray-500 text-sm line-clamp-3 mb-4">
                  {article.description || 'No description available.'}
                </p>
                <div className="flex items-center justify-between">
                  <span className="text-xs text-gray-400">
                    {new Date(article.published_at).toLocaleDateString()}
                  </span>
                  <a
                    href={article.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-1 text-cyan-600 hover:text-cyan-700 text-sm"
                  >
                    Read more <ExternalLink size={14} />
                  </a>
                </div>
              </div>
            </article>
          ))}
        </div>
      )}
    </div>
  );
}