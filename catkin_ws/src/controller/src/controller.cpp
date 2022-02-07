#include "ros/ros.h"
#include "std_msgs/String.h"
#include <sstream>
#include "turtlesim/Pose.h"

class controller {
    public:
        controller(){
            sub = n.subscribe("turtle1/pose", 1000, &controller::callback, this);
            pub = n.advertise<std_msgs::String>("anotherTopic", 1000);
        }

        void callback(const turtlesim::Pose::ConstPtr& msg) {
            std_msgs::String pub_str;
            std::stringstream ss;

            ss << "Controller heard: " << msg->x << ", " << msg->y;

            pub_str.data = ss.str();

            std::cout << pub_str.data.c_str() << std::endl;

            pub.publish(pub_str);
        }
    
    private:
        ros::NodeHandle n;
        ros::Subscriber sub;
        ros::Publisher pub;
};

int main(int argc, char **argv) {
    ros::init(argc, argv, "controller");
    controller ctrl;
    ros::spin();
}