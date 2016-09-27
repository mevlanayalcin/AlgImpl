
public class Test {

    public static void main(String[] args) {
        case1();
    }

    public static void case2() {
        Main_Dinic.WeightedDigraph graph = new Main_Dinic.WeightedDigraph(6);
        graph.addEdge(0, 1, 1);
        graph.addEdge(0, 2, 12);
        graph.addEdge(1, 3, 2);
        graph.addEdge(2, 1, 6);
        graph.addEdge(2, 3, 5);
        graph.addEdge(2, 4, 7);
        graph.addEdge(3, 4, 10);
        graph.addEdge(3, 5, 3);
        graph.addEdge(4, 5, 12);

        Main_Dinic.Dinic flowNet = new Main_Dinic.Dinic(graph, 0, 6 - 1);
        System.out.println(flowNet.computeMaxFlow());
    }
    
    public static void case1() {
        Main_Dinic.WeightedDigraph graph = new Main_Dinic.WeightedDigraph(4);
        graph.addEdge(0, 1, 2);
        graph.addEdge(0, 2, 1);
        graph.addEdge(1, 2, 1);
        graph.addEdge(1, 3, 1);
        graph.addEdge(2, 3, 2);

        Main_Dinic.Dinic flowNet = new Main_Dinic.Dinic(graph, 0, 4 - 1);
        System.out.println(flowNet.computeMaxFlow());
    }
}
