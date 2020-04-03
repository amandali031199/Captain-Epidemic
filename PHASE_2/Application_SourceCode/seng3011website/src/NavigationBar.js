import React, { Component } from "react";
import logo from './img/Logo.png';
import userimg from './img/user.png';
import search from './img/search.png';
import {Navbar,Nav,Form,FormControl,Button,Dropdown} from 'react-bootstrap';


class NavigationBar extends Component {
    render() {
        return (
            <Navbar id='navbar' expand="lg" href='/'>
            <a href='/home' className="d-inline-block align-top" ><img src={logo} id="logo" href='/'alt="Website logo"/> </a>
            <Navbar.Toggle aria-controls="basic-navbar-nav" />
            <Navbar.Collapse id="basic-navbar-nav">
              <Nav className="mr-auto">
                <Nav.Link className='searchbar'>
                  <Form inline>
                    <FormControl type="text" placeholder="Search" className="searchbox" />
                    <Button className='navbutton'> < img className="nav-image" src={search} alt=''/></Button>
                  </Form>
                </Nav.Link>

              </Nav>
              <Dropdown>
                <Dropdown.Toggle variant="success" id="dropdown-custom">
                    <span>
                      <img className="nav-image" src={userimg} alt="user pic"/>
                      Username
                    </span>
                </Dropdown.Toggle>

                <Dropdown.Menu>
                  <Dropdown.Item href="/profile">Profile</Dropdown.Item>
                  <Dropdown.Divider />
                  <Dropdown.Item href="/login">Logout</Dropdown.Item>
                </Dropdown.Menu>
              </Dropdown>


            </Navbar.Collapse>
          </Navbar>
        );
    }
}

export default NavigationBar;