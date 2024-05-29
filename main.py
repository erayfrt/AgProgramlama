import pandas as pd
import webbrowser
from pyvis.network import Network

# CSV dosyasının yolu
file_path = r'C:\Users\enesm\PycharmProjects\pythonProject7\cleaned_movies.csv'

# CSV dosyasını pandas DataFrame'e yükleme
veri_seti = pd.read_csv(file_path).head(50)

# Boş bir ağ oluşturma
net = Network(height='935px', width='100%', notebook=True, bgcolor='#222222', font_color='white')

# Her kategori için renkleri tanımlama
colors = {'Series_Title': '#1f78b4', 'Director': '#33a02c', 'Star1': '#e31a1c', 'Genre': '#ff7f00'}

# Her kategori için düğümleri ekleme
for category in ['Series_Title', 'Director', 'Star1', 'Genre']:
    # Kategorideki benzersiz değerleri al
    unique_values = veri_seti[category].unique()

    # Her benzersiz değer için düğüm oluşturma
    for value in unique_values:
        net.add_node(value, label=value, title=category, color=colors[category], opacity=0.7, size=15)

# Her film için ilişkileri oluşturma
for idx, row in veri_seti.iterrows():
    net.add_edge(row['Series_Title'], row['Director'], title='Yönetmen', color='gray')
    net.add_edge(row['Series_Title'], row['Star1'], title='Başrol', color='gray')
    net.add_edge(row['Series_Title'], row['Genre'], title='Tür', color='gray')

# Fizik seçenekleri için düğmeleri ekleme
net.show_buttons(filter_=['physics'])

# HTML kodunu ekleyerek ağı gösterme
html_content = net.generate_html()
html_content = html_content.replace(
    '</head>',
    '''
    <style>
        #search-container {
            position: fixed;
            top: 10px;
            left: 50%;
            transform: translateX(-50%);
            z-index: 999;
        }
        #search {
            padding: 10px;
            font-size: 16px;
            width: 300px;
            border: 2px solid #ddd;
            border-radius: 5px;
        }
        .modal {
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            overflow: auto;
            background-color: rgb(0,0,0);
            background-color: rgba(0,0,0,0.4);
            padding-top: 60px;
        }
        .modal-content {
            background-color: #fefefe;
            margin: 5% auto;
            padding: 20px;
            border: 1px solid #888;
            width: 50%;
            position: relative;
        }
        .close {
            color: #aaa;
            float: right;
            font-size: 28px;
            font-weight: bold;
            position: absolute;
            top: 10px;
            right: 20px;
        }
        .close:hover,
        .close:focus {
            color: black;
            text-decoration: none;
            cursor: pointer;
        }
    </style>
    </head>
    '''
)

# Film bilgilerini içeren JavaScript kodu
film_info_script = '''
<script type="text/javascript">
    var filmData = {};
'''

# Her film için bilgileri ekleyelim
for idx, row in veri_seti.iterrows():
    film_info_script += f'''
    filmData["{row['Series_Title']}"] = {{
        'Runtime': "{row['Runtime']}",
        'Released_Year': "{row['Released_Year']}",
        'Meta_score': "{row['Meta_score']}",
        'IMDB_Rating': "{row['IMDB_Rating']}",
        'Director': "{row['Director']}",
        'Star1': "{row['Star1']}",
        'Genre': "{row['Genre']}"
    }};
    '''

# Scriptin sonunu kapatalım
film_info_script += '''
    function getTopRecommendations(selectedGenre, selectedTitle) {
        var recommendations = [];
        for (var title in filmData) {
            if (filmData[title]['Genre'] === selectedGenre && title !== selectedTitle) {
                recommendations.push({
                    'title': title,
                    'rating': parseFloat(filmData[title]['IMDB_Rating'])
                });
            }
        }
        recommendations.sort(function(a, b) {
            return b.rating - a.rating;
        });
        return recommendations.slice(0, 3);
    }

    network.on("click", function(params) {
        if (params.nodes.length > 0) {
            var nodeId = params.nodes[0];
            if (filmData[nodeId]) {
                var info = filmData[nodeId];
                var details = "<span class='close'>&times;</span>";
                details += "<h3>" + nodeId + "</h3>";
                details += "<p><strong>Süre:</strong> " + info['Runtime'] + "</p>";
                details += "<p><strong>Vizyon Tarihi:</strong> " + info['Released_Year'] + "</p>";
                details += "<p><strong>Meta Skoru:</strong> " + info['Meta_score'] + "</p>";
                details += "<p><strong>IMDB Puanı:</strong> " + info['IMDB_Rating'] + "</p>";
                details += "<p><strong>Yönetmen:</strong> " + info['Director'] + "</p>";
                details += "<p><strong>Başrol:</strong> " + info['Star1'] + "</p>";

                var recommendations = getTopRecommendations(info['Genre'], nodeId);
                if (recommendations.length > 0) {
                    details += "<h4>Önerilen Filmler:</h4>";
                    details += "<ul>";
                    recommendations.forEach(function(rec) {
                        details += "<li>" + rec.title + " (IMDB Puanı: " + rec.rating.toFixed(1) + ")</li>";
                    });
                    details += "</ul>";
                }

                document.getElementById('modal-content').innerHTML = details;
                document.getElementById('myModal').style.display = "block";

                // Modali kapatma
                document.getElementsByClassName("close")[0].onclick = function() {
                    document.getElementById('myModal').style.display = "none";
                }
                window.onclick = function(event) {
                    if (event.target == document.getElementById('myModal')) {
                        document.getElementById('myModal').style.display = "none";
                    }
                }
            }
        }
    });
</script>
'''

# HTML içeriğine JavaScript kodunu ekleyelim
html_content = html_content.replace('</body>', film_info_script + '</body>')

# Modal HTML kodunu ekleyelim
html_content = html_content.replace(
    '</body>',
    '''
    <div id="search-container">
        <input type="text" id="search" placeholder="Search...">
    </div>
    <div id="myModal" class="modal">
        <div class="modal-content" id="modal-content">
        </div>
    </div>
    <script type="text/javascript">
        document.getElementById('search').addEventListener('input', function() {
            var term = this.value.toLowerCase();
            var nodes = network.body.data.nodes;
            nodes.update(nodes.get().map(function(node) {
                if (!node.originalColor) {
                    node.originalColor = node.color;
                    node.originalSize = node.size;
                    node.originalBorderWidth = node.borderWidth;
                }

                if (term && node.label.toLowerCase().includes(term)) {
                    node.color = '#ffff00';  // Aranan terimi içeren düğümleri sarı renkle vurgula
                    node.size = 30;  // Aranan terimi içeren düğümlerin boyutunu artır
                    node.borderWidth = 3;  // Kenarlık genişliği ekle
                    node.borderWidthSelected = 5;  // Seçildiğinde kenarlık genişliği artır
                } else {
                    node.color = node.originalColor;
                    node.size = node.originalSize;  // Diğer düğümleri normal boyuta getir
                    node.borderWidth = node.originalBorderWidth;  // Kenarlık genişliğini normal hale getir
                }
                return node;
            }));
        });

        // Node'ların orijinal renklerini sakla
        network.on('beforeDrawing', function() {
            network.body.data.nodes.get().forEach(function(node) {
                if (!node.originalColor) {
                    node.originalColor = node.color;
                    node.originalSize = node.size;
                    node.originalBorderWidth = node.borderWidth;
                }
            });
        });
    </script>
    </body>
    '''
)

# HTML içeriğini dosyaya yazma
with open('movie_network_with_search.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

# Oluşturulan HTML dosyasını gösterme
webbrowser.open('movie_network_with_search.html')