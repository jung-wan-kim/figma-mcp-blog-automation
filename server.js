import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { Octokit } from '@octokit/rest';
import dotenv from 'dotenv';

dotenv.config();

const server = new Server({
  name: "github-mcp-server",
  version: "1.0.0",
}, {
  capabilities: {
    tools: {}
  }
});

// GitHub API 클라이언트 초기화
const octokit = new Octokit({
  auth: process.env.GITHUB_TOKEN || 'demo_token'
});

// 브랜치 생성 도구
server.setRequestHandler("tools/create-branch", async (request) => {
  const { repository, branchName, baseBranch = 'main' } = request.params;
  
  try {
    const [owner, repo] = repository.split('/');
    console.log(`🌿 Creating branch: ${branchName} from ${baseBranch}`);
    
    // 베이스 브랜치의 최신 커밋 SHA 가져오기
    const { data: baseRef } = await octokit.rest.git.getRef({
      owner,
      repo,
      ref: `heads/${baseBranch}`
    });
    
    // ?mport { Server } from coimport { StdioServerTransport } from '@modelcontextprotocol/sdk/se oimport { Octokit } from '@octokit/rest';
import dotenv from 'dotenv';

dotenv.coctimport dotenv from 'dotenv';

dotenv.cocc
dotenv.config();

const se,
 
const server =anc  name: "github-mcp-serverht  version: "1.0.0",
}, {
  ry}, {
  capabilitiee}  c      tools: {}
  rr  }
});

// ns})e.
/rorconst octokit = new Octokit({
  auth: me  auth: process.env.GITHUB_Tuc});

// 브랜치 생성 도구
server.setReque  
/});server.setRequestHandler(? const { repository, branchName, baseBranch = 'main' } = request.peq  
  try {
    const [owner, repo] = repository.split('/');
    console. h ad    co b    console.log(`🌿 Creating branch: ${branch[]    
    // 베이스 브랜치의 최신 커밋 SHA 가져오기
    conli   /'    const { data: baseRef } = await octokit.rest.git.getRef//      owner,
      repo,
      ref: `heads/${baseBranch}`
  re      repo,ea      ref: o    });
    
    // ?mport {       
 dy   esimport dotenv from 'dotenv';

dotenv.coctimport dotenv from 'dotenv';

dotenv.cocc
dotenv.config();

const se,
 
const server =anc  name: "giev
dotenv.coctimport dotenv f   
dotenv.cocc
dotenv.config();

const s,
 dotenv.conie
const se,
 
co    
const     }, {
  ry}, {
  capabilitiee}  c      tools: {}
  rr  }
});

//it  rst  capab.a  rr  }
});

// ns})e.
/rorconst  });

/  
/   /rorconsum  auth: me  auth: process.env.GI  
// 브랜치 생성 도구
server.setRequss:server.setReque  
/});ser.n/});server.setRerl  try {
    const [owner, repo] = repository.split('/');
    console. h ad    co b    console.log(`?'    cor.    console. h ad    co b    console.log(`🌿       // 베이스 브랜치의 최신 커밋 SHA 가져오기
    conli   /'  se    conli   /'    const { data: baseRef } = await octokit.r)       repo,
      ref: `heads/${baseBranch}`
  re      repo,ea      ref: o    });
    on      ref: r  re      repo,ea      ref: o        
    // ?mport {       
 dy  es   ng dy   esimport dotenv f);
dotenv.coctimport dotenv from 'dot??dotenv.cocc
dotenv.config();

const s { dotenv.conen
const se,
 
coit  
const restdotenv.coctimport dotenv f   r,dotenv.cocc
dotenv.config();  dotenv.con  
const s,
 dote??  dotenv?onst se,
 
   
co    blobconstwa  ry}, {
  cal(  capabfi  rr  }
});

//it  rst  capab.a   });

/{ 
/ta:});

// ns})e.
/rorconstre
/.gi/rorconsBl
/  
/   /ror  o/ er// 브랜치 생성 도구
server.setRequss:serm(server.setRequss:server.sas/});ser.n/});server.setRerl  try 4'    const [owner, repo] = reposit      console. h ad    co b    console.log(`?' 
     conli   /'  se    conli   /'    const { data: baseRef } = await octokit.r)       repo,
      ref: `heads/${baseBranch}`
  re      repo,ea      ref: o    });
 eT      ref: `heads/${baseBranch}`
  re      repo,ea      ref: o    });
    on      ref: r     re      repo,ea      ref: o  /     on      ref: r  re      repo,ea n    // ?mport {       
 dy  es   ng dy   esimport do   dy  es   ng dy   esimp  dotenv.coctimport dotenv from 'dot?? dotenv.config();

const s { dotenv.conen
const s  
const s { dote치const se,
 
coit  
co   
coit  octoconstesdotenv.config();  dotenv.con  
const s,
 dote??  dof:const s,
 dote??  dotenv?on:  dote??it 
   
co    blobconstwa  urn co    cal(  capabfi  rr  }
} c});

//it  rst  capabha
/   
/{ 
/ta:});

// ns})e..ht/t_u
// ns };/rorconsch/.gi/rorco
 /  
/   /ror ro/ '?erver.setRequss:serm(server.setRequss:s
      conli   /'  se    conli   /'    const { data: baseRef } = await octokit.r)       repo,
      ref: `heads/${baseBranch}`
  re      repo,ea      ref: o    });
 eTas      ref: `heads/${baseBranch}`
  re      repo,ea      ref: o    });
 eT      ref: `headsep  re      repo,ea      ref: o   
 eT      ref: `heads/${baseBranch}`t   re      repo,ea      ref: o    }er    on      ref: r     re      repon  dy  es   ng dy   esimport do   dy  es   ng dy   esimp  dotenv.coctimport dotenv from 'dot?? dotenv.config();

coo.
const s { dotenv.conen
const s  
const s { dote치const se,
 
coit  
co   
coit  octoconstesdotenv.config();retconst s  
const s { dfaconst s    
coit  
co   
coit  octo };
co   );coit ?onst s,
 dote??  dof:const s,
 dote??  dotenvra dote??=  dote??  dotenv?onpo   
co    blobconstwa  urn co  ancoor} c});

//it  rst  capabha
/   
/{ 
/ta:});

// g.
//it
}
/   
/{ 
/ta:});
so/{ er/tr)
// nscat > .env.example << 'EOF'
# GitHub Personal Access Token
# https://github.com/settings/tokens에서 생성
GITHUB_TOKEN=ghp_your_token_here

# 기본 설정
GITHUB_DEFAULT_REPOSITORY=your-username/your-repo
GITHUB_DEFAULT_REVIEWERS=reviewer1,reviewer2
