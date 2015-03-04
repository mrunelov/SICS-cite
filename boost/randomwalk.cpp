#include <iostream>                  // for std::cout
#include <fstream>					 // for file reading
#include <utility>                   // for std::pair
#include <algorithm>                 // for std::for_each
#include <string>
#include <boost/graph/graph_traits.hpp>
#include <boost/graph/adjacency_list.hpp>
//#include <boost/graph/dijkstra_shortest_paths.hpp>
#include <boost/graph/graphml.hpp>

using namespace boost;

typedef boost::adjacency_list<vecS, vecS, directedS,
				  property<vertex_name_t, std::string> > Digraph;	
typedef Digraph::vertex_descriptor Vertex;

int main(int,char*[])
{
	Digraph g;
	boost::dynamic_properties dp;
	dp.property("label", get(vertex_name, g));
	//dp.property("label", get(vertex_label, g));

	std::ifstream graphml_file;
    graphml_file.open("KDD.graphml", std::ifstream::in);
	read_graphml(graphml_file, g, dp);	
    
	std::cout << "Read " << num_vertices(g) << " vertices";
	std::cout << " and " << num_edges(g) << " edges." << std::endl;	
	//write_graphml(std::cout, g, dp, true);

	const int max_iters = 5;
	int i = 0;
	Digraph::adjacency_iterator it, end;
	Vertex start = *(vertices(g).first);	
	std::cout << "Looping vertices for node " << get(vertex_name,g)[start] << "\n" << std::endl;
	for(boost::tie(it, end) = boost::adjacent_vertices(start,g); it != end; ++it) {
		if(i >= max_iters)
			break;
		++i;	
		std::cout << get(vertex_name,g)[*it] << std::endl;
	}	

	//while(i < max_iters) {
	//	++i;
			
	//}

	
	return 0;
}
