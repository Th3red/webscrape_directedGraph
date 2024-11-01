import requests
import webbrowser
from bs4 import BeautifulSoup
import networkx as nx
import matplotlib.pyplot as plt

url = "https://catalog.ucdenver.edu/cu-denver/undergraduate/courses-a-z/csci/"
response = requests.get(url)

soup = BeautifulSoup(response.content, 'html.parser')
courseblock = soup.find_all("div", class_="courseblock")

course_info = []

for course in courseblock:
    course_code = course.find("span", class_="text col-3 detail-code margin--tiny text--huge").get_text(strip=True)
    course_title = course.find("span", class_="text col-8 detail-title margin--tiny text--huge").get_text(strip=True)
    course_hour = course.find("span", class_="text detail-hours_html").get_text(strip=True)
    #course_extra = course.find("span", class_="courseblockextra noindent").get_text(strip=True)
    course_extra = course.find("div", class_="courseblockextra noindent")
    prerequisite = []
    if course_extra:
        a_tags = course_extra.find_all("a", class_="bubblelink")
        for a_tag in a_tags:
            prerequisite.append(a_tag.get_text(strip=True))
            
    course_dict = {"code": course_code, "title": course_title, "hour": course_hour, "prerequisite": prerequisite}
    course_info.append(course_dict)
    
#build html
html_table = """
<!DOCTYPE html>
<html lang="en">
<head>
    <title>CS Department Courses</title>
</head>
<body>
    <h1>CS Department Courses</h1>
    <table>
        <tr>
            <th>Course Code</th>
            <th>Course Title</th>
            <th>Credit Hours</th>
            <th>Prerequisite</th>
        </tr>
"""

for course in course_info:
    prerequisites = ', '.join(course['prerequisite']) if course['prerequisite'] else "None"
    html_table += f"""
        <tr>
            <td>{course['code']}</td>
            <td>{course['title']}</td>
            <td>{course['hour']}</td>
            <td>{prerequisites}</td>
        </tr>
    """
html_table += """
    </table>
    </body>
    </html>
"""
with open("CS_courses.html", "w") as file:
    file.write(html_table)
    
webbrowser.open_new_tab("CS_courses.html")

G = nx.DiGraph()

# Add nodes (courses) to the graph
for course in course_info:
    G.add_node(course['code'], title=course['title'])

# Add edges (prerequisites) to the graph
for course in course_info:
    for prereq in course['prerequisite']:
        G.add_edge(prereq, course['code'])  # Directed edge from prerequisite to course

# Step 4: Draw the graph
plt.figure(figsize=(18, 18))
#pos = nx.spring_layout(G, seed=42, k=0.1)
pos = nx.spring_layout(G, seed=42, k=0.8)

node_sizes = [1000 + 50 * len(G[course]) for course in G.nodes()]
node_colors = [len(G[course]) + 1 for course in G.nodes()] # creates
print(node_colors)
cmap = plt.get_cmap('inferno_r')
nx.draw(G, pos, with_labels=True, node_size=node_sizes, 
        node_color=node_colors, cmap=cmap, font_size=10, font_weight='bold', 
        edge_color='black', arrows=True, alpha=0.7, arrowsize=20)

# Show the graph
plt.title("Course Prerequisite Graph")
plt.axis('on')
plt.show()